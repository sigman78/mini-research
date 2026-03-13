from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mini_research.llm.client import LLMError, complete
from mini_research.llm.cost import CostTracker
from mini_research.llm.models import LLMResponse, Message


def _make_completion(
    content="hello",
    model="openai/gpt-4o-mini",
    prompt_tokens=10,
    completion_tokens=20,
    usage_none=False,
):
    usage = (
        None
        if usage_none
        else SimpleNamespace(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens)
    )
    choice = SimpleNamespace(message=SimpleNamespace(content=content))
    return SimpleNamespace(choices=[choice], usage=usage, model=model)


MESSAGES = [Message(role="user", content="hi")]


@pytest.mark.asyncio
async def test_happy_path_maps_fields():
    completion = _make_completion(
        content="answer", model="openai/gpt-4o-mini", prompt_tokens=5, completion_tokens=15
    )
    with (
        patch(
            "mini_research.llm.client.litellm.acompletion", new=AsyncMock(return_value=completion)
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
    completion = _make_completion()
    tracker = MagicMock(spec=CostTracker)
    with (
        patch(
            "mini_research.llm.client.litellm.acompletion", new=AsyncMock(return_value=completion)
        ),
        patch("mini_research.llm.client.litellm.completion_cost", return_value=0.001),
    ):
        response = await complete(MESSAGES, model="openai/gpt-4o-mini", tracker=tracker)

    tracker.add.assert_called_once_with(response)


@pytest.mark.asyncio
async def test_no_tracker_no_error():
    completion = _make_completion()
    with (
        patch(
            "mini_research.llm.client.litellm.acompletion", new=AsyncMock(return_value=completion)
        ),
        patch("mini_research.llm.client.litellm.completion_cost", return_value=0.0),
    ):
        response = await complete(MESSAGES, model="openai/gpt-4o-mini", tracker=None)

    assert response is not None


@pytest.mark.asyncio
async def test_api_error_raises_llm_error():
    original = RuntimeError("network failure")
    with patch("mini_research.llm.client.litellm.acompletion", new=AsyncMock(side_effect=original)):
        with pytest.raises(LLMError) as exc_info:
            await complete(MESSAGES, model="openai/gpt-4o-mini")

    assert exc_info.value.__cause__ is original


@pytest.mark.asyncio
async def test_cost_fallback_on_completion_cost_error():
    completion = _make_completion()
    with (
        patch(
            "mini_research.llm.client.litellm.acompletion", new=AsyncMock(return_value=completion)
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
    completion = _make_completion(usage_none=True)
    with (
        patch(
            "mini_research.llm.client.litellm.acompletion", new=AsyncMock(return_value=completion)
        ),
        patch("mini_research.llm.client.litellm.completion_cost", return_value=0.0),
    ):
        response = await complete(MESSAGES, model="openai/gpt-4o-mini")

    assert response.input_tokens == 0
    assert response.output_tokens == 0


@pytest.mark.asyncio
async def test_model_fallback_uses_settings_default():
    completion = _make_completion(model="openai/gpt-4o-mini")
    with (
        patch(
            "mini_research.llm.client.litellm.acompletion", new=AsyncMock(return_value=completion)
        ) as mock_acompletion,
        patch("mini_research.llm.client.litellm.completion_cost", return_value=0.0),
    ):
        response = await complete(MESSAGES, model=None)

    called_model = (
        mock_acompletion.call_args.kwargs.get("model") or mock_acompletion.call_args.args[0]
    )
    assert called_model == "openai/gpt-4o-mini"
    assert response.model == "openai/gpt-4o-mini"
