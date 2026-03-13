# M2 — LLM Module

## Goal

Build the provider-agnostic LLM layer that all agents will call, and expose it as a CLI subtool.

## Package Layout

```
src/mini_research/
    llm/
        __init__.py        # exports: complete(), CostTracker, LLMResponse
        client.py          # async LiteLLM wrapper
        cost.py            # CostTracker: accumulate + report session cost
        models.py          # Pydantic: Message, LLMResponse
    cli.py                 # add llm_app Typer sub-app mounted on main app

tests/unit/
    test_llm_client.py     # mock litellm.acompletion, test routing + retries
    test_llm_cost.py       # deterministic cost accumulation tests
```

## Module Design

### llm/models.py

- `Message(BaseModel)`: `role: str`, `content: str`
- `LLMResponse(BaseModel)`: `text: str`, `model: str`, `input_tokens: int`, `output_tokens: int`, `cost_usd: float`

### llm/client.py

Single async function:

```python
async def complete(
    messages: list[Message],
    model: str | None = None,
    settings: Settings | None = None,
    tracker: CostTracker | None = None,
) -> LLMResponse:
```

- Calls `litellm.acompletion()`
- Computes cost via `litellm.completion_cost()`
- Calls `tracker.add(response)` if tracker provided
- Raises `LLMError` (custom exception) on API errors

### llm/cost.py

```python
class CostTracker:
    def add(self, response: LLMResponse) -> None: ...
    def total_usd(self) -> float: ...
    def summary(self) -> str: ...   # human-readable table via Rich
```

### llm/__init__.py

```python
from .client import complete
from .cost import CostTracker
from .models import LLMResponse, Message
```

## CLI Subtool

```
mini-research llm chat PROMPT [--model MODEL] [--system SYSTEM]
mini-research llm models
```

- `chat`: calls `complete()`, prints response + cost with Rich
- `models`: prints the configured model from Settings

## Verification

```bash
uv run mini-research llm --help
uv run mini-research llm models
uv run ruff check .
uv run pytest tests/unit/test_llm_client.py tests/unit/test_llm_cost.py -v
uv run pytest tests/unit/ -v
```
