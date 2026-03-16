from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mini_research.graph import build_graph
from mini_research.llm.cost import CostTracker
from mini_research.state import ResearchState

from .conftest import (
    EVALUATOR_INSUFFICIENT,
    EVALUATOR_SUFFICIENT,
    PLANNER_RESULT,
    REPORTER_MARKDOWN,
    _make_llm_response,
    make_fact,
    make_search_result,
)


@pytest.mark.asyncio
async def test_pipeline_single_iteration_trace(fast_settings):
    reporter_resp = _make_llm_response(REPORTER_MARKDOWN)
    search_results = [make_search_result("https://example.com")]
    facts = {"https://example.com": make_fact("https://example.com")}

    graph = build_graph(settings=fast_settings)
    initial_state = ResearchState(query="What is quantum computing?")

    with (
        patch(
            "mini_research.agents.planner.complete_structured",
            new=AsyncMock(return_value=PLANNER_RESULT),
        ),
        patch(
            "mini_research.agents.evaluator.complete_structured",
            new=AsyncMock(return_value=EVALUATOR_SUFFICIENT),
        ),
        patch("mini_research.agents.reporter.complete", new=AsyncMock(return_value=reporter_resp)),
        patch("mini_research.graph.search_tool", new=AsyncMock(return_value=search_results)),
        patch(
            "mini_research.graph.extract_tool",
            new=AsyncMock(side_effect=lambda url, **kw: facts.get(url)),
        ),
    ):
        trace = []
        async for chunk in graph.astream(initial_state):
            trace.extend(k for k in chunk if not k.startswith("__"))

    assert trace == ["plan", "gather", "evaluate", "report"]


@pytest.mark.asyncio
async def test_pipeline_two_iterations_trace(fast_settings):
    reporter_resp = _make_llm_response(REPORTER_MARKDOWN)
    search_results = [make_search_result("https://example.com")]
    facts = {"https://example.com": make_fact("https://example.com")}

    evaluator_iter = iter([EVALUATOR_INSUFFICIENT, EVALUATOR_SUFFICIENT])

    graph = build_graph(settings=fast_settings)
    initial_state = ResearchState(query="What is quantum computing?")

    with (
        patch(
            "mini_research.agents.planner.complete_structured",
            new=AsyncMock(return_value=PLANNER_RESULT),
        ),
        patch(
            "mini_research.agents.evaluator.complete_structured",
            new=AsyncMock(side_effect=lambda *a, **kw: next(evaluator_iter)),
        ),
        patch("mini_research.agents.reporter.complete", new=AsyncMock(return_value=reporter_resp)),
        patch("mini_research.graph.search_tool", new=AsyncMock(return_value=search_results)),
        patch(
            "mini_research.graph.extract_tool",
            new=AsyncMock(side_effect=lambda url, **kw: facts.get(url)),
        ),
    ):
        trace = []
        async for chunk in graph.astream(initial_state):
            trace.extend(k for k in chunk if not k.startswith("__"))

    assert trace == ["plan", "gather", "evaluate", "gather", "evaluate", "report"]


@pytest.mark.asyncio
async def test_pipeline_max_iterations_exits(fast_settings):
    reporter_resp = _make_llm_response(REPORTER_MARKDOWN)
    search_results = [make_search_result("https://example.com")]
    facts = {"https://example.com": make_fact("https://example.com")}

    graph = build_graph(settings=fast_settings)
    initial_state = ResearchState(query="What is quantum computing?")

    with (
        patch(
            "mini_research.agents.planner.complete_structured",
            new=AsyncMock(return_value=PLANNER_RESULT),
        ),
        patch(
            "mini_research.agents.evaluator.complete_structured",
            new=AsyncMock(return_value=EVALUATOR_INSUFFICIENT),
        ),
        patch("mini_research.agents.reporter.complete", new=AsyncMock(return_value=reporter_resp)),
        patch("mini_research.graph.search_tool", new=AsyncMock(return_value=search_results)),
        patch(
            "mini_research.graph.extract_tool",
            new=AsyncMock(side_effect=lambda url, **kw: facts.get(url)),
        ),
    ):
        trace = []
        async for chunk in graph.astream(initial_state):
            trace.extend(k for k in chunk if not k.startswith("__"))

    assert trace == ["plan", "gather", "evaluate", "gather", "evaluate", "report"]


@pytest.mark.asyncio
async def test_pipeline_final_report_in_state(fast_settings):
    reporter_resp = _make_llm_response(REPORTER_MARKDOWN)
    search_results = [make_search_result("https://example.com")]
    facts = {"https://example.com": make_fact("https://example.com")}

    graph = build_graph(settings=fast_settings)
    initial_state = ResearchState(query="What is quantum computing?")

    with (
        patch(
            "mini_research.agents.planner.complete_structured",
            new=AsyncMock(return_value=PLANNER_RESULT),
        ),
        patch(
            "mini_research.agents.evaluator.complete_structured",
            new=AsyncMock(return_value=EVALUATOR_SUFFICIENT),
        ),
        patch("mini_research.agents.reporter.complete", new=AsyncMock(return_value=reporter_resp)),
        patch("mini_research.graph.search_tool", new=AsyncMock(return_value=search_results)),
        patch(
            "mini_research.graph.extract_tool",
            new=AsyncMock(side_effect=lambda url, **kw: facts.get(url)),
        ),
    ):
        result = await graph.ainvoke(initial_state)

    assert result["final_report"] == REPORTER_MARKDOWN


@pytest.mark.asyncio
async def test_pipeline_visited_urls_deduplication(fast_settings):
    reporter_resp = _make_llm_response(REPORTER_MARKDOWN)
    same_url = "https://same-url.com"
    search_results = [make_search_result(same_url)]
    facts = {same_url: make_fact(same_url)}

    graph = build_graph(settings=fast_settings)
    initial_state = ResearchState(query="What is quantum computing?")

    with (
        patch(
            "mini_research.agents.planner.complete_structured",
            new=AsyncMock(return_value=PLANNER_RESULT),
        ),
        patch(
            "mini_research.agents.evaluator.complete_structured",
            new=AsyncMock(return_value=EVALUATOR_SUFFICIENT),
        ),
        patch("mini_research.agents.reporter.complete", new=AsyncMock(return_value=reporter_resp)),
        patch("mini_research.graph.search_tool", new=AsyncMock(return_value=search_results)),
        patch(
            "mini_research.graph.extract_tool", new=AsyncMock(return_value=facts[same_url])
        ) as mock_extract,
    ):
        await graph.ainvoke(initial_state)

    assert mock_extract.call_count == 1


@pytest.mark.asyncio
async def test_pipeline_tracker_forwarded_to_agents(fast_settings):
    reporter_resp = _make_llm_response(REPORTER_MARKDOWN)
    search_results = [make_search_result("https://example.com")]
    facts = {"https://example.com": make_fact("https://example.com")}

    tracker = MagicMock(spec=CostTracker)
    graph = build_graph(settings=fast_settings, tracker=tracker)
    initial_state = ResearchState(query="What is quantum computing?")

    with (
        patch(
            "mini_research.agents.planner.complete_structured",
            new=AsyncMock(return_value=PLANNER_RESULT),
        ) as mock_planner_cs,
        patch(
            "mini_research.agents.evaluator.complete_structured",
            new=AsyncMock(return_value=EVALUATOR_SUFFICIENT),
        ),
        patch("mini_research.agents.reporter.complete", new=AsyncMock(return_value=reporter_resp)),
        patch("mini_research.graph.search_tool", new=AsyncMock(return_value=search_results)),
        patch(
            "mini_research.graph.extract_tool",
            new=AsyncMock(side_effect=lambda url, **kw: facts.get(url)),
        ),
    ):
        await graph.ainvoke(initial_state)

    _, kwargs = mock_planner_cs.call_args
    assert kwargs.get("tracker") is tracker
