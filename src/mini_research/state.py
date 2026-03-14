from pydantic import BaseModel, Field


class Fact(BaseModel):
    text: str
    source_url: str
    source_title: str = ""


class ResearchState(BaseModel):
    query: str
    search_queries: list[str] = Field(default_factory=list)
    visited_urls: list[str] = Field(default_factory=list)
    gathered_facts: list[Fact] = Field(default_factory=list)
    iteration_count: int = 0
    final_report: str | None = None
