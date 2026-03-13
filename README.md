# Mini Research

Self hosted mini deep research tool based on LangGraph, LiteLLM, backed by configurable search backend.

Pure context engineering, multi-agent powered, LLM powered deep research experimental pipeline -
base for prompt engineering and gardening agents

```txt
 ___ ___  ____  ____   ____        ____     ___  _____   ___   ____  ____      __  __ __    ___  ____  
|   |   ||    ||    \ |    |      |    \   /  _]/ ___/  /  _] /    ||    \    /  ]|  |  |  /  _]|    \ 
| _   _ | |  | |  _  | |  | _____ |  D  ) /  [_(   \_  /  [_ |  o  ||  D  )  /  / |  |  | /  [_ |  D  )
|  \_/  | |  | |  |  | |  ||     ||    / |    _]\__  ||    _]|     ||    /  /  /  |  _  ||    _]|    / 
|   |   | |  | |  |  | |  ||_____||    \ |   [_ /  \ ||   [_ |  _  ||    \ /   \_ |  |  ||   [_ |    \ 
|   |   | |  | |  |  | |  |       |  .  \|     |\    ||     ||  |  ||  .  \\     ||  |  ||     ||  .  \
|___|___||____||__|__||____|      |__|\_||_____| \___||_____||__|__||__|\_| \____||__|__||_____||__|\_|
```                                                                                                       

---

## Install

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone <repo>
cd mini-research
uv sync
cp .env.example .env   # add your API keys
```

Set at least one provider key in `.env`:

```
OPENAI_API_KEY=sk-...
# or ANTHROPIC_API_KEY / any LiteLLM-supported provider
```

## Usage

```bash
# Run a research query
uv run mini-research research "your query"

# Test the LLM layer
uv run mini-research llm models
uv run mini-research llm chat "Hello" --model openai/gpt-4o-mini

# Run tests
uv run pytest tests/unit/
```