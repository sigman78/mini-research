# M3: Search and Scrape Layer

## Overview

M3 implements the search and scrape infrastructure for mini-research. This layer enables flexible provider selection and configuration for discovering and extracting content from web sources.

## Components

### Search Providers
- **DuckDuckGo**: Default, free search provider
- **Brave**: API-based search with premium features (requires API key)
- **Reddit**: Stub provider for Reddit-specific search

### Scrape Providers
- **Trafilatura**: Default HTML parsing and content extraction
- **Jina**: Alternative scrape provider for enhanced content extraction
- **Crawl4AI**: Reserved for future use

### Configuration
New settings in `config.py`:
- `search_provider`: Select active search provider (default: "duckduckgo")
- `scrape_provider`: Select active scrape provider (default: "trafilatura")
- `search_max_results`: Limit results per search (default: 5)
- `search_delay_seconds`: Rate limiting between requests (default: 0.5)

### CLI Sub-apps
- `search`: Query web sources via configured provider
- `scrape`: Extract content from URLs via configured provider
- `crawl`: Combined search and scrape workflow

## Integration Points

Search and scrape outputs feed into the Research Pipeline:
1. Planner generates sub-queries
2. Search tool returns URLs
3. Scrape tool extracts facts with citations
4. Evaluator checks coverage and loops if needed
5. Reporter assembles final report

## Testing Strategy

- Unit tests for parsing logic
- VCR.py for captured network responses
- Mock LLM outputs for agent tests
- 100% reproducible pipeline tests
