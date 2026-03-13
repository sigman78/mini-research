# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv run ruff check .          # lint
uv run ruff format .         # format
uv run pytest                # all tests
uv run pytest tests/path/to_test.py::test_name  # single test
```

## Architecture

Self-hosted deep research CLI tool. LangGraph orchestrates a multi-agent pipeline; LiteLLM provides provider-agnostic LLM access.

**Pipeline flow:**
1. User query → Planner Agent (enriches query, generates 3-5 sub-queries, composes research plan)
2. Search tool → returns top URLs per sub-query
3. Extractor tool → scrapes pages, extracts facts, builds working memory with citations
4. Evaluator Agent → checks coverage; if insufficient, generates new search vectors and loops
5. Reporter Agent → drafts final Markdown report with inline citations

**Core state** (`ResearchState` TypedDict): `query`, `search_queries`, `visited_urls`, `gathered_facts`, `iteration_count`, `final_report`

**Modules:**
- LLM API: provider-agnostic interface, config, cost tracking, routing (via LiteLLM)
- Search/scrape providers: DuckDuckGo, Brave, Reddit search → trafilatura, Jina, crawl4AI, Reddit API scrapers
- Working memory: queries, sources, visited links, facts + URLs
- Agents: planner, evaluator, reporter (prompts are easily configurable)
- Orchestrator: LangGraph

## Coding Rules

- No inline comments unless critical explanation or specialized docstrings
- No unicode or emojis in source code or messages
- Pydantic for main data classes; type annotations on major interfaces/APIs; avoid over-specific types
- Before implementing a feature: write a plan at `docs/nn-task-desc.md`; after verified, move to `docs/archive/`

## Testing Strategy

- Deterministic parts (parsing, extraction): unit tests
- Pipeline tests: no real LLM calls or network — use `VCR.py` for captured crawl data, mock LLM outputs, record/compare agent traces
- Goal: 100% reproducible pipeline tests
