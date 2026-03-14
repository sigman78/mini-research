# CLI interface

I like how cli structured right now in general but we need to improve both on inputs as well as on outputs

Add support '@' notation for text args, i.e. `llm chat "Question" OR llm chat @question-file.txt`

```
uv run mini-research llm models

uv run mini-research llm chat -m|--model {model-name} -s|--system {system-prompt} "Text"

uv run mini-research scrape -c|--scraper {scrape-provider-name} "URL"

uv run mini-research search -s|--seacher {search-provider-name} -l|--limit {max-num-results} "Query"

# Note -o|--out option is required
uv run mini-research research -i|--iter {max-research-iterations} -l|--limit {max-searches-per-iter} -c|--scraper {scrape-provider-name} -o|--out {result-file-name} "Query"
```