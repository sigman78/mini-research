import litellm

from ..config import Settings
from .cost import CostTracker
from .models import LLMResponse, Message


class LLMError(Exception):
    pass


async def complete(
    messages: list[Message],
    model: str | None = None,
    settings: Settings | None = None,
    tracker: CostTracker | None = None,
) -> LLMResponse:
    if settings is None:
        settings = Settings()
    resolved_model = model or settings.litellm_model
    raw_messages = [{"role": m.role, "content": m.content} for m in messages]
    try:
        completion = await litellm.acompletion(model=resolved_model, messages=raw_messages)
    except Exception as exc:
        raise LLMError(str(exc)) from exc
    choice = completion.choices[0]
    usage = completion.usage
    try:
        cost = litellm.completion_cost(completion_response=completion)
    except Exception:
        cost = 0.0
    response = LLMResponse(
        text=choice.message.content or "",
        model=completion.model or resolved_model,
        input_tokens=usage.prompt_tokens if usage is not None else 0,
        output_tokens=usage.completion_tokens if usage is not None else 0,
        cost_usd=cost,
    )
    if tracker is not None:
        tracker.add(response)
    return response
