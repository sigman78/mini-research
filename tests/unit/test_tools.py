from unittest.mock import AsyncMock, patch

import pytest

from mini_research.scrape import ScrapeError
from mini_research.scrape.models import ScrapeResult
from mini_research.search.models import SearchResult
from mini_research.state import Fact
from mini_research.tools import extract_tool, search_tool


@pytest.mark.asyncio
async def test_search_tool_returns_results():
    results = [SearchResult(url="https://example.com", title="Ex", snippet="snip")]
    with patch("mini_research.tools.search", new=AsyncMock(return_value=results)):
        out = await search_tool("test query")
    assert out == results


@pytest.mark.asyncio
async def test_search_tool_passes_settings():
    from mini_research.config import Settings

    settings = Settings()
    results = []
    with patch("mini_research.tools.search", new=AsyncMock(return_value=results)) as mock_search:
        await search_tool("q", settings=settings)
    _, kwargs = mock_search.call_args
    assert kwargs.get("settings") is settings


@pytest.mark.asyncio
async def test_extract_tool_returns_fact():
    result = ScrapeResult(text="some text content", title="Page Title", url="https://example.com")
    with patch("mini_research.tools.scrape", new=AsyncMock(return_value=result)):
        fact = await extract_tool("https://example.com")
    assert isinstance(fact, Fact)
    assert fact.source_url == "https://example.com"
    assert fact.source_title == "Page Title"
    assert fact.text == "some text content"


@pytest.mark.asyncio
async def test_extract_tool_empty_text_returns_none():
    result = ScrapeResult(text="", title="Page", url="https://example.com")
    with patch("mini_research.tools.scrape", new=AsyncMock(return_value=result)):
        fact = await extract_tool("https://example.com")
    assert fact is None


@pytest.mark.asyncio
async def test_extract_tool_scrape_error_returns_none():
    with patch("mini_research.tools.scrape", new=AsyncMock(side_effect=ScrapeError("failed"))):
        fact = await extract_tool("https://example.com")
    assert fact is None


@pytest.mark.asyncio
async def test_extract_tool_truncates_long_text():
    long_text = "x" * 5000
    result = ScrapeResult(text=long_text, title="Long Page", url="https://example.com")
    with patch("mini_research.tools.scrape", new=AsyncMock(return_value=result)):
        fact = await extract_tool("https://example.com")
    assert fact is not None
    assert fact.text == "x" * 4000
