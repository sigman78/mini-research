from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from ..config import Settings
from ..llm.client import complete_structured
from ..llm.cost import CostTracker
from ..state import ResearchState
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
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
    return await complete_structured(messages, PlannerResult, settings=settings, tracker=tracker)
