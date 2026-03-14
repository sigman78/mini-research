import os
from collections.abc import Callable

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from mini_research.agents import run_evaluator, run_planner, run_reporter
from mini_research.config import Settings
from mini_research.llm.cost import CostTracker
from mini_research.state import ResearchState
from mini_research.tools import extract_tool, search_tool


async def plan_node(
    state: ResearchState,
    settings: Settings,
    tracker: CostTracker,
) -> dict:
    result = await run_planner(state, settings=settings, tracker=tracker)
    return {"query": result.enriched_query, "search_queries": result.sub_queries}


async def gather_node(
    state: ResearchState,
    settings: Settings,
    tracker: CostTracker,
    on_scrape_progress: Callable[[int, int], None] | None = None,
) -> dict:
    visited = set(state.visited_urls)
    new_urls: list[str] = []

    for query in state.search_queries:
        results = await search_tool(query, settings=settings)
        for result in results:
            if result.url not in visited:
                visited.add(result.url)
                new_urls.append(result.url)

    new_facts = []
    total = len(new_urls)
    for i, url in enumerate(new_urls):
        if on_scrape_progress:
            on_scrape_progress(i, total)
        fact = await extract_tool(url, settings=settings)
        if fact is not None:
            new_facts.append(fact)
    if on_scrape_progress and total > 0:
        on_scrape_progress(total, total)

    return {
        "visited_urls": state.visited_urls + new_urls,
        "gathered_facts": state.gathered_facts + new_facts,
    }


async def evaluate_node(
    state: ResearchState,
    settings: Settings,
    tracker: CostTracker,
) -> dict:
    result = await run_evaluator(state, settings=settings, tracker=tracker)
    existing = set(state.search_queries)
    deduped_new = [q for q in result.new_queries if q not in existing]
    return {
        "coverage_sufficient": result.sufficient,
        "iteration_count": state.iteration_count + 1,
        "search_queries": state.search_queries + deduped_new,
    }


async def report_node(
    state: ResearchState,
    settings: Settings,
    tracker: CostTracker,
) -> dict:
    text = await run_reporter(state, settings=settings, tracker=tracker)
    return {"final_report": text}


def route_after_evaluate(settings: Settings):
    def _route(state: ResearchState) -> str:
        if state.coverage_sufficient or state.iteration_count >= settings.max_research_iterations:
            return "report"
        return "gather"

    return _route


def build_graph(
    settings: Settings | None = None,
    tracker: CostTracker | None = None,
    on_scrape_progress: Callable[[int, int], None] | None = None,
) -> CompiledStateGraph:
    if settings is None:
        settings = Settings()
    if tracker is None:
        tracker = CostTracker()

    if settings.langsmith_tracing and settings.langsmith_api_key:
        os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
        os.environ["LANGSMITH_TRACING"] = "true"
        os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project

    async def _plan(state: ResearchState) -> dict:
        return await plan_node(state, settings, tracker)

    async def _gather(state: ResearchState) -> dict:
        return await gather_node(state, settings, tracker, on_scrape_progress)

    async def _evaluate(state: ResearchState) -> dict:
        return await evaluate_node(state, settings, tracker)

    async def _report(state: ResearchState) -> dict:
        return await report_node(state, settings, tracker)

    graph = StateGraph(ResearchState)
    graph.add_node("plan", _plan)
    graph.add_node("gather", _gather)
    graph.add_node("evaluate", _evaluate)
    graph.add_node("report", _report)

    graph.add_edge(START, "plan")
    graph.add_edge("plan", "gather")
    graph.add_edge("gather", "evaluate")
    graph.add_conditional_edges("evaluate", route_after_evaluate(settings))
    graph.add_edge("report", END)

    return graph.compile()
