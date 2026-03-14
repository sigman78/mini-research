# M7: CLI & UX + LangSmith Tracing

## Goal

Fix two CLI UX gaps and wire up LangSmith tracing.

## Changes

### 1. config.py — LangSmith fields

Add `langsmith_api_key`, `langsmith_tracing`, `langsmith_project` to Settings.

### 2. graph.py — LangSmith env setup

At the top of `build_graph()`, set `os.environ` vars when tracing is enabled and an API key is present.

### 3. cli.py — restructure and add progress spinner

- Remove `search_app` and `scrape_app` sub-typers; register `search` and `scrape` as top-level commands.
- Add Rich `Status` spinner to `research` command that updates per LangGraph node.

### 4. .env.example — document LangSmith vars

### 5. Tests

- `tests/unit/test_graph.py` — 3 tests for LangSmith env var setup.
- `tests/unit/test_cli.py` — 6 tests for CLI commands (search, scrape, research).
