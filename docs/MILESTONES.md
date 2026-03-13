# Milestones

| # | Milestone | Status | Description |
|---|-----------|--------|-------------|
| M1 | **Project Scaffold** | done | pyproject.toml, src layout, stub modules, CLI entry, smoke tests |
| M2 | **LLM Module** | done | LiteLLM wrapper, Pydantic config, cost tracker, async interface |
| M3 | **Search & Scrape Layer** | done | DuckDuckGo/Brave/Reddit(stub) search + trafilatura/Jina scrape; provider protocols, routers, CLI sub-apps, 20 unit tests |
| M4 | **State & Working Memory** | - | ResearchState (Pydantic), WorkingMemory class, citation tracking |
| M5 | **Agent Implementations** | - | Planner, Evaluator, Reporter — async callables with prompt files, mock-LLM unit tests |
| M6 | **LangGraph Orchestration** | - | graph.py with evaluation loop, pipeline integration tests (VCR + mock LLM) |
| M7 | **CLI & UX** | - | Typer commands (`research`, `search`, `scrape`), Rich progress display, Markdown output |
| M8 | **Testing Hardening** | - | VCR cassettes, golden fixture pipeline test, pre-commit hooks |
