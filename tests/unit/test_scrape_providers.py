from unittest.mock import AsyncMock, patch

import pytest
import respx
from httpx import Response

from mini_research.config import Settings
from mini_research.scrape.errors import ScrapeError
from mini_research.scrape.jina import JinaProvider
from mini_research.scrape.models import ScrapeResult
from mini_research.scrape.router import scrape
from mini_research.scrape.trafilatura_provider import TrafilaturaProvider


@pytest.mark.asyncio
async def test_trafilatura_maps_text():
    with (
        patch(
            "mini_research.scrape.trafilatura_provider.trafilatura.fetch_url",
            return_value="<html>",
        ),
        patch(
            "mini_research.scrape.trafilatura_provider.trafilatura.extract",
            return_value="extracted text",
        ),
        patch(
            "mini_research.scrape.trafilatura_provider.trafilatura.bare_extraction",
            return_value={"title": ""},
        ),
    ):
        result = await TrafilaturaProvider().scrape("https://example.com")
    assert result.text == "extracted text"


@pytest.mark.asyncio
async def test_trafilatura_handles_extract_none():
    with (
        patch(
            "mini_research.scrape.trafilatura_provider.trafilatura.fetch_url",
            return_value="<html>",
        ),
        patch(
            "mini_research.scrape.trafilatura_provider.trafilatura.extract",
            return_value=None,
        ),
        patch(
            "mini_research.scrape.trafilatura_provider.trafilatura.bare_extraction",
            return_value={"title": ""},
        ),
    ):
        result = await TrafilaturaProvider().scrape("https://example.com")
    assert result.text == ""


@pytest.mark.asyncio
async def test_trafilatura_captures_title():
    with (
        patch(
            "mini_research.scrape.trafilatura_provider.trafilatura.fetch_url",
            return_value="<html>",
        ),
        patch(
            "mini_research.scrape.trafilatura_provider.trafilatura.extract",
            return_value="text",
        ),
        patch(
            "mini_research.scrape.trafilatura_provider.trafilatura.bare_extraction",
            return_value={"title": "Page Title"},
        ),
    ):
        result = await TrafilaturaProvider().scrape("https://example.com")
    assert result.title == "Page Title"


@pytest.mark.asyncio
@respx.mock
async def test_jina_maps_text():
    respx.get("https://r.jina.ai/https://example.com").mock(
        return_value=Response(200, text="page content")
    )
    result = await JinaProvider().scrape("https://example.com")
    assert result.text == "page content"


@pytest.mark.asyncio
@respx.mock
async def test_jina_sends_accept_header():
    route = respx.get("https://r.jina.ai/https://example.com").mock(
        return_value=Response(200, text="content")
    )
    await JinaProvider().scrape("https://example.com")
    assert route.calls.last.request.headers["accept"] == "text/plain"


@pytest.mark.asyncio
@respx.mock
async def test_jina_raises_on_http_error():
    respx.get("https://r.jina.ai/https://example.com").mock(return_value=Response(500))
    with pytest.raises(ScrapeError):
        await JinaProvider().scrape("https://example.com")


@pytest.mark.asyncio
async def test_scrape_router_dispatches_trafilatura():
    expected = ScrapeResult(url="https://example.com", text="text", title="Title")
    with patch.object(TrafilaturaProvider, "scrape", new=AsyncMock(return_value=expected)):
        result = await scrape("https://example.com", settings=Settings())
    assert result == expected


@pytest.mark.asyncio
async def test_scrape_router_dispatches_jina():
    expected = ScrapeResult(url="https://example.com", text="jina text", title="")
    with patch.object(JinaProvider, "scrape", new=AsyncMock(return_value=expected)):
        result = await scrape("https://example.com", provider="jina", settings=Settings())
    assert result == expected


@pytest.mark.asyncio
async def test_scrape_router_unknown_provider_raises():
    with pytest.raises(ScrapeError, match="unknown provider"):
        await scrape("https://example.com", provider="unknown", settings=Settings())
