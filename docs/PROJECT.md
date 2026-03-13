# Mini-research project summary

## Tools
- `uv` package manager
- `ruff` checks
- `pytest` tests

## Planned features

- CLI based tool
- LLM API integration via env or toml config
- Configurable web searcher and scraper tools
- Rate-limiting for sensetive external APIs
- Async tools and agent processing
- Visual cli clues of whats going on currently in text (progress bar, time etc)
- Markdown article research output
- Internal tools (like search or scrape) are exposed to user via CLI

## Pipeline overview

- User Query
- Planner Agent - generates "Research plan"
  - Enriches original query
  - Generates 3-5 sub-requests to explore
  - Composes final research plan
- Search tool - executes searches, returns top URLs
- Extractor tool - ingests scraped text, extracts relevant facts, builds a working memory with citations (URLs)
- Evaluator agent - checks user query against workign memory. 
  - If not enough info collected, generates new more specific research vector and repeats search cycle
  - Otherwise proceeds next
- Reporter agent - Drafts the final report document using working memory. Injects inline citations/references
- Easily configurable prompts for agents

## Modules and parts

- LLM API: provider agnostic interface, configuration, cost tracking, routing
- Search & scrape providers (with plugins): 
  - query to url list: duckduckgo, brave search, reddit search
  - scrapers: trafilatura, https://r.jina.ai, crawl4AI, reddit API
- Working memory: stores queries, collected sources, visited links, facts and urls
- Agents: Query analyzer and research planner, collected material quality assessor, plan retargeter, report composer
- Orchestrator: LangGraph to direct agents

## Internal state

Very simplified application internal state representation

```py
class ResearchState(TypedDict):
    query: str
    search_queries: List[str] # Queries yet to be searched
    visited_urls: List[str]
    gathered_facts: List[str] # Facts extracted from pages
    iteration_count: int
    final_report: str
```

## Documentation

Stored at `/docs/` path

- @docs/PROJECT.md (this) global project description
- @docs/nn-task-desc.md - planned ordered task in work
- @docs/archive/nn-task-desc.md - completed tasks

## Goals

- Playground of agent orchestration and langgraph study
- Example of how to properly test agent based pipelines
- Practical CLI tool
- Simple(fied) practical architecture design: no abstractions for the sake of the abstractions

## Non-goals

- Production quality researcher tool
- DB integration
- Elaborate architecture design

## Problem points / possible pitfalls

- Rate limited APIs
- Bot protection (403s)
- Reseach loop detection (keep agents focused)
- Hallucinations - confirm citated URLs
- Reproducible pipeline testing

## Testing

All already deterministic parts should have unit tests - parsing, text extraction etc.

For pipeline we need establish reproducible and 100% deterministic tests - which means no real LLM calls or internet.
- Capture snapshot of crawled data manually or via `VCR.py` tool which would be used in tests
- Mock LLM outputs
- Record agent and tool processing 'traces' and compare to desired standard

## Benchmarking

TBD probably LangSmith/Langfuse based eval kit