from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from mini_research.agents.planner import PlannerResult
from mini_research.llm.client import LLMError, complete, complete_structured
from mini_research.llm.cost import CostTracker
from mini_research.llm.models import LLMResponse


def _make_ai_message(
    content="hello",
    model="openai/gpt-4o-mini",
    input_tokens=10,
    output_tokens=20,
    usage_none=False,
):
    usage_metadata = (
        None
        if usage_none
        else {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
        }
    )
    return AIMessage(
        content=content,
        response_metadata={"model": model},
        usage_metadata=usage_metadata,
    )


MESSAGES = [HumanMessage(content="hi")]


@pytest.mark.asyncio
async def test_happy_path_maps_fields():
    ai_message = _make_ai_message(
        content="answer", model="openai/gpt-4o-mini", input_tokens=5, output_tokens=15
    )
    with (
        patch(
            "mini_research.llm.client.ChatLiteLLM.ainvoke", new=AsyncMock(return_value=ai_message)
        ),
        patch("mini_research.llm.client.litellm.cost_per_token", return_value=(0.0012, 0.0)),
    ):
        response = await complete(MESSAGES, model="openai/gpt-4o-mini")

    assert isinstance(response, LLMResponse)
    assert response.text == "answer"
    assert response.model == "openai/gpt-4o-mini"
    assert response.input_tokens == 5
    assert response.output_tokens == 15
    assert response.cost_usd == pytest.approx(0.0012)


@pytest.mark.asyncio
async def test_tracker_add_called():
    ai_message = _make_ai_message()
    tracker = MagicMock(spec=CostTracker)
    with (
        patch(
            "mini_research.llm.client.ChatLiteLLM.ainvoke", new=AsyncMock(return_value=ai_message)
        ),
        patch("mini_research.llm.client.litellm.cost_per_token", return_value=(0.001, 0.0)),
    ):
        response = await complete(MESSAGES, model="openai/gpt-4o-mini", tracker=tracker)

    tracker.add.assert_called_once_with(response)


@pytest.mark.asyncio
async def test_no_tracker_no_error():
    ai_message = _make_ai_message()
    with (
        patch(
            "mini_research.llm.client.ChatLiteLLM.ainvoke", new=AsyncMock(return_value=ai_message)
        ),
        patch("mini_research.llm.client.litellm.cost_per_token", return_value=(0.0, 0.0)),
    ):
        response = await complete(MESSAGES, model="openai/gpt-4o-mini", tracker=None)

    assert response is not None


@pytest.mark.asyncio
async def test_api_error_raises_llm_error():
    original = RuntimeError("network failure")
    with patch("mini_research.llm.client.ChatLiteLLM.ainvoke", new=AsyncMock(side_effect=original)):
        with pytest.raises(LLMError) as exc_info:
            await complete(MESSAGES, model="openai/gpt-4o-mini")

    assert exc_info.value.__cause__ is original


@pytest.mark.asyncio
async def test_cost_fallback_on_completion_cost_error():
    ai_message = _make_ai_message()
    with (
        patch(
            "mini_research.llm.client.ChatLiteLLM.ainvoke", new=AsyncMock(return_value=ai_message)
        ),
        patch(
            "mini_research.llm.client.litellm.cost_per_token",
            side_effect=Exception("pricing unavailable"),
        ),
    ):
        response = await complete(MESSAGES, model="openai/gpt-4o-mini")

    assert response.cost_usd == 0.0


@pytest.mark.asyncio
async def test_usage_none_tokens_are_zero():
    ai_message = _make_ai_message(usage_none=True)
    with (
        patch(
            "mini_research.llm.client.ChatLiteLLM.ainvoke", new=AsyncMock(return_value=ai_message)
        ),
        patch("mini_research.llm.client.litellm.cost_per_token", return_value=(0.0, 0.0)),
    ):
        response = await complete(MESSAGES, model="openai/gpt-4o-mini")

    assert response.input_tokens == 0
    assert response.output_tokens == 0


@pytest.mark.asyncio
@pytest.mark.skip(reason="model is baked into ChatLiteLLM constructor, needs dedicated mock")
async def test_model_fallback_uses_settings_default():
    pass


# ---------------------------------------------------------------------------
# complete_structured tests
# ---------------------------------------------------------------------------


def _make_structured_result(parsed: PlannerResult, ai_message: AIMessage) -> dict:
    return {"raw": ai_message, "parsed": parsed, "parsing_error": None}


@pytest.mark.asyncio
async def test_complete_structured_happy_path():
    ai_message = _make_ai_message(input_tokens=8, output_tokens=12)
    expected = PlannerResult(enriched_query="What is quantum computing?", sub_queries=["a", "b"])
    chain_result = _make_structured_result(expected, ai_message)

    mock_chain = MagicMock()
    mock_chain.ainvoke = AsyncMock(return_value=chain_result)

    with patch(
        "mini_research.llm.client.ChatLiteLLM.with_structured_output", return_value=mock_chain
    ):
        result = await complete_structured(MESSAGES, PlannerResult, model="openai/gpt-4o-mini")

    assert result is expected
    assert result.enriched_query == "What is quantum computing?"


@pytest.mark.asyncio
async def test_complete_structured_tracker_called():
    ai_message = _make_ai_message(input_tokens=8, output_tokens=12)
    expected = PlannerResult(enriched_query="q", sub_queries=["x"])
    chain_result = _make_structured_result(expected, ai_message)
    tracker = MagicMock(spec=CostTracker)

    mock_chain = MagicMock()
    mock_chain.ainvoke = AsyncMock(return_value=chain_result)

    with (
        patch(
            "mini_research.llm.client.ChatLiteLLM.with_structured_output", return_value=mock_chain
        ),
        patch("mini_research.llm.client.litellm.cost_per_token", return_value=(0.0005, 0.0)),
    ):
        await complete_structured(
            MESSAGES, PlannerResult, model="openai/gpt-4o-mini", tracker=tracker
        )

    tracker.add.assert_called_once()
    recorded: LLMResponse = tracker.add.call_args.args[0]
    assert recorded.input_tokens == 8
    assert recorded.output_tokens == 12


@pytest.mark.asyncio
async def test_complete_structured_parsing_error_raises_llm_error():
    ai_message = _make_ai_message()
    chain_result = {"raw": ai_message, "parsed": None, "parsing_error": ValueError("bad schema")}

    mock_chain = MagicMock()
    mock_chain.ainvoke = AsyncMock(return_value=chain_result)

    with patch(
        "mini_research.llm.client.ChatLiteLLM.with_structured_output", return_value=mock_chain
    ):
        with pytest.raises(LLMError, match="parsing error"):
            await complete_structured(MESSAGES, PlannerResult, model="openai/gpt-4o-mini")


@pytest.mark.asyncio
async def test_complete_structured_api_error_raises_llm_error():
    mock_chain = MagicMock()
    mock_chain.ainvoke = AsyncMock(side_effect=RuntimeError("connection refused"))

    with patch(
        "mini_research.llm.client.ChatLiteLLM.with_structured_output", return_value=mock_chain
    ):
        with pytest.raises(LLMError):
            await complete_structured(MESSAGES, PlannerResult, model="openai/gpt-4o-mini")
