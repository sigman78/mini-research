import warnings

import litellm
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_litellm import ChatLiteLLM
from pydantic import BaseModel

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


def _build_response(ai_message: AIMessage, resolved_model: str) -> LLMResponse:
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
    return LLMResponse(
        text=ai_message.content or "",
        model=model_name,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_usd=cost,
    )


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
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", "Pydantic serializer warnings", UserWarning)
            ai_message: AIMessage = await llm.ainvoke(_to_lc_messages(messages))
    except Exception as exc:
        raise LLMError(str(exc)) from exc
    response = _build_response(ai_message, resolved_model)
    if tracker is not None:
        tracker.add(response)
    return response


async def complete_structured[T: BaseModel](
    messages: list[Message],
    schema: type[T],
    model: str | None = None,
    settings: Settings | None = None,
    tracker: CostTracker | None = None,
) -> T:
    if settings is None:
        settings = Settings()
    resolved_model = model or settings.litellm_model
    llm = ChatLiteLLM(model=resolved_model)
    chain = llm.with_structured_output(schema, method="function_calling", include_raw=True)
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", "Pydantic serializer warnings", UserWarning)
            result = await chain.ainvoke(_to_lc_messages(messages))
    except Exception as exc:
        raise LLMError(str(exc)) from exc
    if result.get("parsing_error"):
        raise LLMError(f"Structured output parsing error: {result['parsing_error']}")
    ai_message: AIMessage = result["raw"]
    response = _build_response(ai_message, resolved_model)
    if tracker is not None:
        tracker.add(response)
    return result["parsed"]
