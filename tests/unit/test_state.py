import pytest
from pydantic import ValidationError

from mini_research.state import Fact, ResearchState


def test_fact_defaults():
    fact = Fact(text="some text", source_url="http://example.com")
    assert fact.source_title == ""


def test_fact_requires_text_and_url():
    with pytest.raises(ValidationError):
        Fact(text="only text")
    with pytest.raises(ValidationError):
        Fact(source_url="http://example.com")


def test_research_state_defaults():
    state = ResearchState(query="test query")
    assert state.search_queries == []
    assert state.visited_urls == []
    assert state.gathered_facts == []
    assert state.iteration_count == 0
    assert state.final_report is None


def test_research_state_requires_query():
    with pytest.raises(ValidationError):
        ResearchState()


def test_research_state_accepts_facts():
    facts = [
        Fact(text="fact one", source_url="http://a.com"),
        Fact(text="fact two", source_url="http://b.com"),
    ]
    state = ResearchState(query="q", gathered_facts=facts)
    assert len(state.gathered_facts) == 2
    assert state.gathered_facts[0].text == "fact one"


def test_research_state_rejects_bad_facts():
    with pytest.raises(ValidationError):
        ResearchState(query="q", gathered_facts=[{"not_valid": True}])
