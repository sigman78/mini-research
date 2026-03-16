from pydantic import BaseModel

from ..config import Settings
from ..llm.client import complete
from ..llm.cost import CostTracker
from ..llm.models import Message
from ..state import ResearchState
from ._parse import extract_json
from .prompts import load_prompt


class PlannerResult(BaseModel):
    enriched_query: str
    sub_queries: list[str]


async def run_planner(
    state: ResearchState,
    settings: Settings | None = None,
    tracker: CostTracker | None = None,
) -> PlannerResult:
    system_prompt = load_prompt("planner_system")
    user_prompt = load_prompt("planner_user", query=state.query)
    messages = [
        Message(role="system", content=system_prompt),
        Message(role="user", content=user_prompt),
    ]
    response = await complete(messages, settings=settings, tracker=tracker)
    json_text = extract_json(response.text)
    return PlannerResult.model_validate_json(json_text)
