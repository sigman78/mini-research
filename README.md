# Mini Research

Self hosted mini deep research tool based on LangGraph, LiteLLM, backed by configurable search backend.

Pure context engineering, multi-agent powered, LLM powered deep research experimental pipeline -
base for prompt engineering and gardening agents

```txt
 ___ ___  ____  ____   ____        ____     ___  _____   ___   ____  ____      __  __ __ 
|   |   ||    ||    \ |    |      |    \   /  _]/ ___/  /  _] /    ||    \    /  ]|  |  |
| _   _ | |  | |  _  | |  | _____ |  D  ) /  [_(   \_  /  [_ |  o  ||  D  )  /  / |  |  |
|  \_/  | |  | |  |  | |  ||     ||    / |    _]\__  ||    _]|     ||    /  /  /  |  _  |
|   |   | |  | |  |  | |  ||_____||    \ |   [_ /  \ ||   [_ |  _  ||    \ /   \_ |  |  |
|   |   | |  | |  |  | |  |       |  .  \|     |\    ||     ||  |  ||  .  \\     ||  |  |
|___|___||____||__|__||____|      |__|\_||_____| \___||_____||__|__||__|\_| \____||__|__|
```                                                                                                       

Sample result on [Notable locations and activities to visit by train lovers in SoCal?](https://gist.github.com/sigman78/05dd59226dccfbdd987bb72683491a36)

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
# Run a research query (-o is required)
uv run mini-research research "your query" -o report.md
uv run mini-research research "your query" -o report.md -i 3 -l 5 -c jina

# Search and scrape
uv run mini-research search "query" -s brave -l 10
uv run mini-research scrape "https://example.com" -c trafilatura

# LLM utilities
uv run mini-research llm models
uv run mini-research llm chat "Hello" -m openai/gpt-4o-mini
uv run mini-research llm chat @prompt.txt -m openai/gpt-4o -s "You are a helpful assistant"

# Text args accept @file notation
uv run mini-research research @query.txt -o report.md

# Run tests
uv run pytest tests/unit/
```
