import litellm
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_litellm import ChatLiteLLM

from ..config import Settings
from .cost import CostTracker
from .models import LLMResponse, Message

_ROLE_MAP = {
    "system": SystemMessage,
    "user": HumanMessage,
    "assistant": AIMessage,
}


class LLMError(Exception):
    pass


def _to_lc_messages(messages: list[Message]) -> list:
    return [_ROLE_MAP.get(m.role, HumanMessage)(content=m.content) for m in messages]


async def complete(
    messages: list[Message],
    model: str | None = None,
    settings: Settings | None = None,
    tracker: CostTracker | None = None,
) -> LLMResponse:
    if settings is None:
        settings = Settings()
    resolved_model = model or settings.litellm_model
    llm = ChatLiteLLM(model=resolved_model)
    try:
        ai_message: AIMessage = await llm.ainvoke(_to_lc_messages(messages))
    except Exception as exc:
        raise LLMError(str(exc)) from exc
    usage = ai_message.usage_metadata or {}
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)
    model_name = (ai_message.response_metadata or {}).get("model", resolved_model)
    try:
        cost = litellm.completion_cost(
            model=resolved_model,
            prompt_tokens=input_tokens,
            completion_tokens=output_tokens,
        )
    except Exception:
        cost = 0.0
    response = LLMResponse(
        text=ai_message.content or "",
        model=model_name,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_usd=cost,
    )
    if tracker is not None:
        tracker.add(response)
    return response
