from pydantic import BaseModel, Field

from ..config import Settings
from ..llm.client import complete_structured
from ..llm.cost import CostTracker
from ..llm.models import Message
from ..state import ResearchState
from .prompts import load_prompt


class EvaluatorResult(BaseModel):
    sufficient: bool
    new_queries: list[str] = Field(default_factory=list)
    reasoning: str = ""


def _facts_summary(state: ResearchState) -> str:
    if not state.gathered_facts:
        return "No facts gathered yet."
    lines = []
    for i, fact in enumerate(state.gathered_facts, 1):
        title = fact.source_title or fact.source_url
        lines.append(f"{i}. [{title}] {fact.text}")
    return "\n".join(lines)


async def run_evaluator(
    state: ResearchState,
    settings: Settings | None = None,
    tracker: CostTracker | None = None,
) -> EvaluatorResult:
    summary = _facts_summary(state)
    searched = "\n".join(f"{i}. {q}" for i, q in enumerate(state.search_queries, 1))
    system_prompt = load_prompt("evaluator_system")
    user_prompt = load_prompt(
        "evaluator_user",
        query=state.query,
        iteration=str(state.iteration_count),
        searched_queries=searched or "None yet.",
        facts_summary=summary,
    )
    messages = [
        Message(role="system", content=system_prompt),
        Message(role="user", content=user_prompt),
    ]
    return await complete_structured(messages, EvaluatorResult, settings=settings, tracker=tracker)
