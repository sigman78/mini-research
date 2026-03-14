from mini_research.memory import WorkingMemory
from mini_research.state import ResearchState


def test_add_query_accumulates():
    mem = WorkingMemory("q")
    mem.add_query("alpha")
    mem.add_query("beta")
    assert mem.queries == ["alpha", "beta"]


def test_add_query_deduplicates():
    mem = WorkingMemory("q")
    mem.add_query("alpha")
    mem.add_query("alpha")
    assert mem.queries == ["alpha"]


def test_add_query_preserves_order():
    mem = WorkingMemory("q")
    for q in ["c", "a", "b"]:
        mem.add_query(q)
    assert mem.queries == ["c", "a", "b"]


def test_mark_visited_and_has_visited():
    mem = WorkingMemory("q")
    mem.mark_visited("http://example.com")
    assert mem.has_visited("http://example.com")


def test_has_visited_returns_false_for_unknown():
    mem = WorkingMemory("q")
    assert not mem.has_visited("http://unknown.com")


def test_add_fact_accumulates():
    mem = WorkingMemory("q")
    mem.add_fact("fact one", "http://a.com")
    mem.add_fact("fact two", "http://b.com")
    assert len(mem.facts) == 2


def test_add_fact_captures_citation():
    mem = WorkingMemory("q")
    mem.add_fact("detail", "http://src.com", source_title="My Source")
    fact = mem.facts[0]
    assert fact.text == "detail"
    assert fact.source_url == "http://src.com"
    assert fact.source_title == "My Source"


def test_to_state_snapshot():
    mem = WorkingMemory("research query")
    mem.add_query("sub-query 1")
    mem.mark_visited("http://page.com")
    mem.add_fact("a fact", "http://page.com", "Page Title")

    state = mem.to_state()

    assert isinstance(state, ResearchState)
    assert state.query == "research query"
    assert state.search_queries == ["sub-query 1"]
    assert "http://page.com" in state.visited_urls
    assert len(state.gathered_facts) == 1
    assert state.gathered_facts[0].source_title == "Page Title"
    assert state.iteration_count == 0
    assert state.final_report is None


def test_to_state_passes_iteration_and_report():
    mem = WorkingMemory("q")
    state = mem.to_state(iteration_count=3, final_report="Report text")
    assert state.iteration_count == 3
    assert state.final_report == "Report text"
