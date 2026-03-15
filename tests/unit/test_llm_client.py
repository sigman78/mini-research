from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.messages import AIMessage

from mini_research.llm.client import LLMError, complete
from mini_research.llm.cost import CostTracker
from mini_research.llm.models import LLMResponse, Message


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


MESSAGES = [Message(role="user", content="hi")]


@pytest.mark.asyncio
async def test_happy_path_maps_fields():
    ai_message = _make_ai_message(
        content="answer", model="openai/gpt-4o-mini", input_tokens=5, output_tokens=15
    )
    with (
        patch(
            "mini_research.llm.client.ChatLiteLLM.ainvoke", new=AsyncMock(return_value=ai_message)
        ),
        patch("mini_research.llm.client.litellm.completion_cost", return_value=0.0012),
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
        patch("mini_research.llm.client.litellm.completion_cost", return_value=0.001),
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
        patch("mini_research.llm.client.litellm.completion_cost", return_value=0.0),
    ):
        response = await complete(MESSAGES, model="openai/gpt-4o-mini", tracker=None)

    assert response is not None


@pytest.mark.asyncio
async def test_api_error_raises_llm_error():
    original = RuntimeError("network failure")
    with patch(
        "mini_research.llm.client.ChatLiteLLM.ainvoke", new=AsyncMock(side_effect=original)
    ):
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
            "mini_research.llm.client.litellm.completion_cost",
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
        patch("mini_research.llm.client.litellm.completion_cost", return_value=0.0),
    ):
        response = await complete(MESSAGES, model="openai/gpt-4o-mini")

    assert response.input_tokens == 0
    assert response.output_tokens == 0


@pytest.mark.asyncio
@pytest.mark.skip(reason="model is baked into ChatLiteLLM constructor, needs dedicated mock")
async def test_model_fallback_uses_settings_default():
    pass
