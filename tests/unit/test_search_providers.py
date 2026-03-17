from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import respx
from httpx import Response

from mini_research.config import Settings
from mini_research.search.brave import BraveProvider
from mini_research.search.duckduckgo import DuckDuckGoProvider
from mini_research.search.errors import SearchError
from mini_research.search.models import SearchResult
from mini_research.search.reddit import RedditProvider
from mini_research.search.router import search


@pytest.mark.asyncio
async def test_duckduckgo_maps_fields():
    mock_ddgs = MagicMock()
    mock_ddgs.return_value.text.return_value = [
        {"title": "T", "href": "https://example.com", "body": "S"}
    ]
    with patch("mini_research.search.duckduckgo.DDGS", mock_ddgs):
        results = await DuckDuckGoProvider().search("query", max_results=5)
    assert len(results) == 1
    assert results[0] == SearchResult(title="T", url="https://example.com", snippet="S")


@pytest.mark.asyncio
async def test_duckduckgo_respects_max_results():
    mock_ddgs = MagicMock()
    mock_ddgs.return_value.text.return_value = []
    with patch("mini_research.search.duckduckgo.DDGS", mock_ddgs):
        await DuckDuckGoProvider().search("query", max_results=3)
    mock_ddgs.return_value.text.assert_called_once_with("query", max_results=3)


@pytest.mark.asyncio
async def test_duckduckgo_empty_results():
    mock_ddgs = MagicMock()
    mock_ddgs.return_value.text.return_value = []
    with patch("mini_research.search.duckduckgo.DDGS", mock_ddgs):
        results = await DuckDuckGoProvider().search("query", max_results=5)
    assert results == []


@pytest.mark.asyncio
@respx.mock
async def test_brave_maps_fields():
    respx.get("https://api.search.brave.com/res/v1/web/search").mock(
        return_value=Response(
            200,
            json={"web": {"results": [{"title": "T", "url": "https://b.com", "description": "D"}]}},
        )
    )
    provider = BraveProvider(settings=Settings(brave_api_key="testkey"))
    results = await provider.search("query", max_results=5)
    assert len(results) == 1
    assert results[0] == SearchResult(title="T", url="https://b.com", snippet="D")


@pytest.mark.asyncio
@respx.mock
async def test_brave_raises_on_http_error():
    respx.get("https://api.search.brave.com/res/v1/web/search").mock(return_value=Response(401))
    provider = BraveProvider(settings=Settings(brave_api_key="testkey"))
    with pytest.raises(SearchError):
        await provider.search("query", max_results=5)


@pytest.mark.asyncio
async def test_brave_raises_if_no_api_key():
    with pytest.raises(SearchError, match="brave_api_key not configured"):
        await search("query", provider="brave", settings=Settings(brave_api_key=None))


@pytest.mark.asyncio
async def test_reddit_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        await RedditProvider().search("query", max_results=5)


@pytest.mark.asyncio
async def test_router_dispatches_duckduckgo():
    expected = [SearchResult(title="T", url="https://example.com", snippet="S")]
    with (
        patch(
            "mini_research.search.router.asyncio.sleep",
            new=AsyncMock(),
        ),
        patch.object(DuckDuckGoProvider, "search", new=AsyncMock(return_value=expected)),
    ):
        results = await search("query", provider="duckduckgo", settings=Settings())
    assert results == expected


@pytest.mark.asyncio
@respx.mock
async def test_router_dispatches_brave():
    expected = [SearchResult(title="T", url="https://b.com", snippet="D")]
    with (
        patch("mini_research.search.router.asyncio.sleep", new=AsyncMock()),
        patch.object(BraveProvider, "search", new=AsyncMock(return_value=expected)),
    ):
        results = await search(
            "query",
            provider="brave",
            settings=Settings(brave_api_key="key"),
        )
    assert results == expected


@pytest.mark.asyncio
async def test_router_sleeps_before_search():
    mock_sleep = AsyncMock()
    mock_ddgs = MagicMock()
    mock_ddgs.return_value.text.return_value = []
    settings = Settings(search_delay_seconds=1.5)
    with (
        patch("mini_research.search.router.asyncio.sleep", new=mock_sleep),
        patch("mini_research.search.duckduckgo.DDGS", mock_ddgs),
    ):
        await search("query", provider="duckduckgo", settings=settings)
    mock_sleep.assert_called_once_with(1.5)


@pytest.mark.asyncio
async def test_router_unknown_provider_raises():
    with pytest.raises(SearchError, match="unknown provider"):
        await search("query", provider="xyz", settings=Settings())
