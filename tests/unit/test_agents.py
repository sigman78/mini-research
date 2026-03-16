from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mini_research.agents.evaluator import EvaluatorResult, run_evaluator
from mini_research.agents.planner import PlannerResult, run_planner
from mini_research.agents.prompts import load_prompt
from mini_research.agents.reporter import run_reporter
from mini_research.llm.cost import CostTracker
from mini_research.llm.models import LLMResponse
from mini_research.state import Fact, ResearchState


def _make_response(text: str) -> LLMResponse:
    return LLMResponse(
        text=text, model="test-model", input_tokens=10, output_tokens=20, cost_usd=0.0
    )


def _make_state(**kwargs) -> ResearchState:
    defaults = {"query": "What is quantum computing?"}
    defaults.update(kwargs)
    return ResearchState(**defaults)


# ---------------------------------------------------------------------------
# Prompt loader tests
# ---------------------------------------------------------------------------


def test_load_prompt_substitutes_vars():
    result = load_prompt("planner_user", query="test query")
    assert "test query" in result


def test_load_prompt_missing_var_raises():
    with pytest.raises(KeyError):
        load_prompt("planner_user")


def test_load_prompt_unknown_name_raises():
    with pytest.raises(FileNotFoundError):
        load_prompt("nonexistent_prompt_xyz", query="x")


# ---------------------------------------------------------------------------
# Planner tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_planner_parses_json():
    state = _make_state()
    expected = PlannerResult(
        enriched_query="What is quantum computing and how does it differ from classical computing?",
        sub_queries=[
            "quantum computing fundamentals and qubits",
            "quantum vs classical computing comparison",
            "quantum computing real-world applications",
        ],
    )
    with patch(
        "mini_research.agents.planner.complete_structured", new=AsyncMock(return_value=expected)
    ):
        result = await run_planner(state)

    assert isinstance(result, PlannerResult)
    assert len(result.sub_queries) == 3
    assert "quantum" in result.enriched_query.lower()


@pytest.mark.asyncio
async def test_run_planner_passes_tracker():
    state = _make_state()
    tracker = MagicMock(spec=CostTracker)
    expected = PlannerResult(enriched_query="q", sub_queries=["a"])
    with patch(
        "mini_research.agents.planner.complete_structured",
        new=AsyncMock(return_value=expected),
    ) as mock_cs:
        await run_planner(state, tracker=tracker)

    _, kwargs = mock_cs.call_args
    assert kwargs.get("tracker") is tracker


# ---------------------------------------------------------------------------
# Evaluator tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_evaluator_sufficient():
    state = _make_state()
    expected = EvaluatorResult(
        sufficient=True,
        new_queries=[],
        reasoning="Enough facts collected to write a comprehensive report.",
    )
    with patch(
        "mini_research.agents.evaluator.complete_structured", new=AsyncMock(return_value=expected)
    ):
        result = await run_evaluator(state)

    assert isinstance(result, EvaluatorResult)
    assert result.sufficient is True
    assert result.new_queries == []


@pytest.mark.asyncio
async def test_run_evaluator_insufficient_with_queries():
    state = _make_state()
    expected = EvaluatorResult(
        sufficient=False,
        new_queries=["quantum error correction", "quantum supremacy milestones"],
        reasoning="Missing coverage on error correction and recent milestones.",
    )
    with patch(
        "mini_research.agents.evaluator.complete_structured", new=AsyncMock(return_value=expected)
    ):
        result = await run_evaluator(state)

    assert result.sufficient is False
    assert len(result.new_queries) == 2
    assert "quantum error correction" in result.new_queries


@pytest.mark.asyncio
async def test_run_evaluator_defaults():
    state = _make_state()
    expected = EvaluatorResult(sufficient=False)
    with patch(
        "mini_research.agents.evaluator.complete_structured", new=AsyncMock(return_value=expected)
    ):
        result = await run_evaluator(state)

    assert result.sufficient is False
    assert result.new_queries == []
    assert result.reasoning == ""


# ---------------------------------------------------------------------------
# Reporter tests
# ---------------------------------------------------------------------------

REPORTER_MARKDOWN = """# Quantum Computing Research Report

## Summary

Quantum computing uses qubits to perform computations.

## Key Findings

- Quantum computers can solve certain problems exponentially faster.
- [Example Source](https://example.com)

## Conclusion

Quantum computing is a transformative technology.
"""


@pytest.mark.asyncio
async def test_run_reporter_returns_text():
    state = _make_state()
    mock_response = _make_response(REPORTER_MARKDOWN)
    with patch("mini_research.agents.reporter.complete", new=AsyncMock(return_value=mock_response)):
        result = await run_reporter(state)

    assert isinstance(result, str)
    assert "Quantum Computing" in result


@pytest.mark.asyncio
async def test_run_reporter_builds_facts_summary():
    fact = Fact(
        text="Qubits can be 0 and 1 simultaneously.",
        source_url="https://example.com",
        source_title="Example",
    )
    state = _make_state(gathered_facts=[fact])
    mock_response = _make_response(REPORTER_MARKDOWN)
    with patch(
        "mini_research.agents.reporter.complete", new=AsyncMock(return_value=mock_response)
    ) as mock_complete:
        await run_reporter(state)

    call_messages = mock_complete.call_args.args[0]
    user_content = call_messages[1].content
    assert "Qubits can be 0 and 1 simultaneously" in user_content


@pytest.mark.asyncio
async def test_run_reporter_passes_tracker():
    state = _make_state()
    tracker = MagicMock(spec=CostTracker)
    mock_response = _make_response(REPORTER_MARKDOWN)
    with patch(
        "mini_research.agents.reporter.complete", new=AsyncMock(return_value=mock_response)
    ) as mock_complete:
        await run_reporter(state, tracker=tracker)

    _, kwargs = mock_complete.call_args
    assert kwargs.get("tracker") is tracker
