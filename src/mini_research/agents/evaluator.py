from pydantic import BaseModel, Field

from ..config import Settings
from ..llm.client import complete
from ..llm.cost import CostTracker
from ..llm.models import Message
from ..state import ResearchState
from ._parse import extract_json
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
    system_prompt = load_prompt(
        "evaluator",
        query=state.query,
        facts_summary=summary,
        iteration=str(state.iteration_count),
    )
    messages = [
        Message(role="system", content=system_prompt),
        Message(role="user", content="Evaluate the current research coverage."),
    ]
    response = await complete(messages, settings=settings, tracker=tracker)
    json_text = extract_json(response.text)
    return EvaluatorResult.model_validate_json(json_text)
