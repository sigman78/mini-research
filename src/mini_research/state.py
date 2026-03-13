from typing import TypedDict


class ResearchState(TypedDict):
    query: str
    search_queries: list[str]
    visited_urls: list[str]
    gathered_facts: list[dict]
    iteration_count: int
    final_report: str | None
