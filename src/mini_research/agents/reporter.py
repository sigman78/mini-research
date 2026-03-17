from langchain_core.messages import HumanMessage, SystemMessage

from ..config import Settings
from ..llm.client import complete
from ..llm.cost import CostTracker
from ..state import ResearchState
from .prompts import load_prompt


def _format_facts(state: ResearchState) -> str:
    if not state.gathered_facts:
        return "No facts gathered."
    lines = []
    for fact in state.gathered_facts:
        title = fact.source_title or fact.source_url
        lines.append(f"- {fact.text} (source: [{title}]({fact.source_url}))")
    return "\n".join(lines)


async def run_reporter(
    state: ResearchState,
    settings: Settings | None = None,
    tracker: CostTracker | None = None,
) -> str:
    facts = _format_facts(state)
    system_prompt = load_prompt("reporter_system")
    user_prompt = load_prompt("reporter_user", query=state.query, facts=facts)
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
    response = await complete(messages, settings=settings, tracker=tracker)
    return response.text
