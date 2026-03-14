from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mini_research.agents.evaluator import EvaluatorResult
from mini_research.agents.planner import PlannerResult
from mini_research.config import Settings
from mini_research.graph import evaluate_node, gather_node, plan_node, report_node
from mini_research.llm.cost import CostTracker
from mini_research.search.models import SearchResult
from mini_research.state import Fact, ResearchState


def _make_state(**kwargs) -> ResearchState:
    defaults = {"query": "test query"}
    defaults.update(kwargs)
    return ResearchState(**defaults)


def _make_settings() -> Settings:
    return Settings(search_delay_seconds=0, max_research_iterations=2)


@pytest.mark.asyncio
async def test_plan_node_updates_state():
    state = _make_state()
    settings = _make_settings()
    tracker = CostTracker()
    planner_result = PlannerResult(enriched_query="enriched test query", sub_queries=["q1", "q2"])
    with patch("mini_research.graph.run_planner", new=AsyncMock(return_value=planner_result)):
        result = await plan_node(state, settings, tracker)
    assert result["query"] == "enriched test query"
    assert result["search_queries"] == ["q1", "q2"]


@pytest.mark.asyncio
async def test_plan_node_passes_tracker():
    state = _make_state()
    settings = _make_settings()
    tracker = MagicMock(spec=CostTracker)
    planner_result = PlannerResult(enriched_query="q", sub_queries=[])
    with patch(
        "mini_research.graph.run_planner", new=AsyncMock(return_value=planner_result)
    ) as mock_planner:
        await plan_node(state, settings, tracker)
    _, kwargs = mock_planner.call_args
    assert kwargs.get("tracker") is tracker


@pytest.mark.asyncio
async def test_gather_node_skips_visited_urls():
    visited_url = "https://already-visited.com"
    state = _make_state(
        search_queries=["q1"],
        visited_urls=[visited_url],
    )
    settings = _make_settings()
    tracker = CostTracker()
    search_results = [SearchResult(url=visited_url, title="Visited", snippet="")]
    with patch("mini_research.graph.search_tool", new=AsyncMock(return_value=search_results)):
        with patch("mini_research.graph.extract_tool", new=AsyncMock()) as mock_extract:
            await gather_node(state, settings, tracker)
    mock_extract.assert_not_called()


@pytest.mark.asyncio
async def test_gather_node_handles_extract_none():
    state = _make_state(search_queries=["q1"])
    settings = _make_settings()
    tracker = CostTracker()
    search_results = [SearchResult(url="https://example.com", title="Ex", snippet="")]
    with patch("mini_research.graph.search_tool", new=AsyncMock(return_value=search_results)):
        with patch("mini_research.graph.extract_tool", new=AsyncMock(return_value=None)):
            result = await gather_node(state, settings, tracker)
    assert result["gathered_facts"] == []


@pytest.mark.asyncio
async def test_gather_node_accumulates_facts():
    existing_fact = Fact(text="existing", source_url="https://old.com")
    state = _make_state(
        search_queries=["q1"],
        gathered_facts=[existing_fact],
    )
    settings = _make_settings()
    tracker = CostTracker()
    search_results = [
        SearchResult(url="https://url1.com", title="U1", snippet=""),
        SearchResult(url="https://url2.com", title="U2", snippet=""),
    ]
    new_fact1 = Fact(text="fact1", source_url="https://url1.com")
    new_fact2 = Fact(text="fact2", source_url="https://url2.com")
    with patch("mini_research.graph.search_tool", new=AsyncMock(return_value=search_results)):
        with patch(
            "mini_research.graph.extract_tool", new=AsyncMock(side_effect=[new_fact1, new_fact2])
        ):
            result = await gather_node(state, settings, tracker)
    assert len(result["gathered_facts"]) == 3


@pytest.mark.asyncio
async def test_evaluate_node_sets_sufficient():
    state = _make_state(search_queries=["q1"])
    settings = _make_settings()
    tracker = CostTracker()
    eval_result = EvaluatorResult(sufficient=True, new_queries=[])
    with patch("mini_research.graph.run_evaluator", new=AsyncMock(return_value=eval_result)):
        result = await evaluate_node(state, settings, tracker)
    assert result["coverage_sufficient"] is True
    assert result["iteration_count"] == 1


@pytest.mark.asyncio
async def test_evaluate_node_appends_deduped_queries():
    state = _make_state(search_queries=["existing_query"])
    settings = _make_settings()
    tracker = CostTracker()
    eval_result = EvaluatorResult(sufficient=False, new_queries=["existing_query", "brand_new"])
    with patch("mini_research.graph.run_evaluator", new=AsyncMock(return_value=eval_result)):
        result = await evaluate_node(state, settings, tracker)
    assert result["search_queries"] == ["existing_query", "brand_new"]


@pytest.mark.asyncio
async def test_report_node_sets_final_report():
    state = _make_state()
    settings = _make_settings()
    tracker = CostTracker()
    report_text = "# Final Report\n\nSome content."
    with patch("mini_research.graph.run_reporter", new=AsyncMock(return_value=report_text)):
        result = await report_node(state, settings, tracker)
    assert result["final_report"] == report_text
