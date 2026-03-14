# M5: Agent Implementations

## Goal

Implement Planner, Evaluator, and Reporter agents as async callables wrapping the existing
`complete()` interface. Prompts live in standalone `.md` files loaded via `importlib.resources`.

## Approach

- `src/mini_research/prompts/` — new sub-package; plain Markdown files with `{variable}` placeholders
- `src/mini_research/agents/prompts.py` — `load_prompt(name, **vars)` using `importlib.resources`
- `src/mini_research/agents/_parse.py` — `extract_json(text)` regex helper
- `src/mini_research/agents/planner.py` — `PlannerResult`, `run_planner()`
- `src/mini_research/agents/evaluator.py` — `EvaluatorResult`, `run_evaluator()`
- `src/mini_research/agents/reporter.py` — `run_reporter()` returning `str`

## Result Models

```python
class PlannerResult(BaseModel):
    enriched_query: str
    sub_queries: list[str]

class EvaluatorResult(BaseModel):
    sufficient: bool
    new_queries: list[str] = Field(default_factory=list)
    reasoning: str = ""
```

## Shared Agent Pattern

1. `load_prompt(name, **vars)` → system prompt
2. Build `[system_msg, user_msg]`
3. `await complete(messages, settings=settings, tracker=tracker)`
4. Extract JSON from fenced block, `model_validate_json()` → result
5. Return typed result (Reporter returns raw `str`)

## Tests

~12 unit tests in `tests/unit/test_agents.py`, all mock-LLM via `AsyncMock`.

## Status: implemented
