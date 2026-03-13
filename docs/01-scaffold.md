# M1 — Project Scaffold

## Goal

Initialize the uv project, create the src layout, stub all modules, add CLI entry point,
configure tooling, and add smoke tests.

## Steps

1. Initialize uv project and add dependencies
2. Create directory tree with __init__.py stubs
3. Implement core stub modules (state, config, memory, graph, tools, cli)
4. Add .env.example
5. Add .pre-commit-config.yaml
6. Add smoke tests (tests/unit/test_scaffold.py)

## Verification

```bash
uv sync --dev
uv run mini-research --help        # exits 0, shows research command
uv run ruff check .                # no errors
uv run pytest tests/unit/test_scaffold.py  # 3 passed
```
