import pytest

from mini_research.llm.cost import CostTracker
from mini_research.llm.models import LLMResponse


def _resp(
    cost: float, model: str = "openai/gpt-4o-mini", input_tokens: int = 10, output_tokens: int = 20
) -> LLMResponse:
    return LLMResponse(
        text="t", model=model, input_tokens=input_tokens, output_tokens=output_tokens, cost_usd=cost
    )


def test_empty_tracker_total_is_zero():
    tracker = CostTracker()
    assert tracker.total_usd() == 0.0


def test_single_response_total():
    tracker = CostTracker()
    tracker.add(_resp(0.0042))
    assert tracker.total_usd() == pytest.approx(0.0042)


def test_multiple_responses_total_sums():
    tracker = CostTracker()
    tracker.add(_resp(0.001))
    tracker.add(_resp(0.002))
    tracker.add(_resp(0.003))
    assert tracker.total_usd() == pytest.approx(0.006)


def test_summary_returns_non_empty_string():
    tracker = CostTracker()
    tracker.add(_resp(0.001, model="openai/gpt-4o-mini", input_tokens=5, output_tokens=10))
    result = tracker.summary()
    assert isinstance(result, str)
    assert len(result) > 0


def test_add_accumulates_all_responses():
    tracker = CostTracker()
    costs = [0.001, 0.005, 0.002, 0.003]
    for c in costs:
        tracker.add(_resp(c))
    assert tracker.total_usd() == pytest.approx(sum(costs))
