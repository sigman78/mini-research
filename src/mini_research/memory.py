from mini_research.state import Fact, ResearchState


class WorkingMemory:
    """Accumulates search queries, source URLs, visited links, and extracted facts
    with citations during a research session. Acts as the shared mutable context
    passed between pipeline stages."""

    def __init__(self, query: str) -> None:
        self._query = query
        self._queries: list[str] = []
        self._queries_set: set[str] = set()
        self._visited: set[str] = set()
        self._facts: list[Fact] = []

    def add_query(self, query: str) -> None:
        if query not in self._queries_set:
            self._queries.append(query)
            self._queries_set.add(query)

    def mark_visited(self, url: str) -> None:
        self._visited.add(url)

    def has_visited(self, url: str) -> bool:
        return url in self._visited

    def add_fact(self, text: str, source_url: str, source_title: str = "") -> None:
        self._facts.append(Fact(text=text, source_url=source_url, source_title=source_title))

    @property
    def queries(self) -> list[str]:
        return list(self._queries)

    @property
    def visited_urls(self) -> list[str]:
        return list(self._visited)

    @property
    def facts(self) -> list[Fact]:
        return list(self._facts)

    def to_state(self, iteration_count: int = 0, final_report: str | None = None) -> ResearchState:
        return ResearchState(
            query=self._query,
            search_queries=self.queries,
            visited_urls=self.visited_urls,
            gathered_facts=self.facts,
            iteration_count=iteration_count,
            final_report=final_report,
        )
