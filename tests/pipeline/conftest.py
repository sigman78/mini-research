import pytest

from mini_research.config import Settings
from mini_research.llm.models import LLMResponse
from mini_research.search.models import SearchResult
from mini_research.state import Fact

PLANNER_JSON = """```json
{
  "enriched_query": "What is quantum computing and how does it work?",
  "sub_queries": [
    "quantum computing fundamentals",
    "quantum vs classical computing"
  ]
}
```"""

EVALUATOR_SUFFICIENT_JSON = """```json
{
  "sufficient": true,
  "new_queries": [],
  "reasoning": "Sufficient coverage gathered."
}
```"""

EVALUATOR_INSUFFICIENT_JSON = """```json
{
  "sufficient": false,
  "new_queries": ["quantum error correction"],
  "reasoning": "Need more coverage."
}
```"""

REPORTER_MARKDOWN = """# Quantum Computing Research Report

## Summary

Quantum computing uses qubits to perform computations.

## Conclusion

Quantum computing is a transformative technology.
"""


@pytest.fixture
def fast_settings() -> Settings:
    return Settings(search_delay_seconds=0, max_research_iterations=2)


def _make_llm_response(text: str) -> LLMResponse:
    return LLMResponse(
        text=text, model="test-model", input_tokens=10, output_tokens=20, cost_usd=0.001
    )


def make_search_result(url: str) -> SearchResult:
    return SearchResult(url=url, title="Test Page", snippet="test snippet")


def make_fact(url: str) -> Fact:
    return Fact(text="Some fact text.", source_url=url, source_title="Test Page")
