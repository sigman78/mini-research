# M4: State & Working Memory

## Goal

Replace the bare TypedDict stub in `state.py` and the empty class in `memory.py` with full
Pydantic-validated models and a `WorkingMemory` accumulator class. Add citation tracking via
a `Fact` model.

## Scope

- `src/mini_research/state.py` — `Fact` + `ResearchState` Pydantic models
- `src/mini_research/memory.py` — `WorkingMemory` accumulator with dedup + `to_state()`
- `src/mini_research/__init__.py` — export new public symbols
- `tests/unit/test_state.py` — 6 unit tests
- `tests/unit/test_memory.py` — 9 unit tests

## Design Decisions

- `gathered_facts` moves from `list[dict]` to `list[Fact]` for typed citation tracking
- `final_report` defaults to `None` (was bare `str` in stub)
- `WorkingMemory` stores visited URLs in a `set` internally for O(1) dedup
- `add_query` preserves insertion order via list + set membership check
- `to_state()` snapshots current memory into `ResearchState` for LangGraph handoff
- LangGraph 0.2+ supports Pydantic BaseModel as node state natively

## Verification

```bash
uv run pytest tests/unit/test_state.py tests/unit/test_memory.py -v
uv run pytest
uv run ruff check . && uv run ruff format --check .
```
