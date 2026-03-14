from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import respx
from httpx import Response

from mini_research.config import Settings
from mini_research.scrape.crawl4ai_provider import Crawl4aiProvider
from mini_research.scrape.errors import ScrapeError
from mini_research.scrape.jina import JinaProvider
from mini_research.scrape.models import ScrapeResult
from mini_research.scrape.router import scrape
from mini_research.scrape.trafilatura_provider import TrafilaturaProvider


def _meta(data: dict) -> MagicMock:
    m = MagicMock()
    m.as_dict.return_value = data
    return m


def _crawl_result(success: bool, raw_markdown: str = "", title: str = "") -> MagicMock:
    result = MagicMock()
    result.success = success
    result.error_message = None
    result.markdown = MagicMock()
    result.markdown.raw_markdown = raw_markdown
    result.metadata = {"title": title}
    return result


def _crawler_ctx(crawl_result: MagicMock) -> MagicMock:
    crawler = MagicMock()
    crawler.arun = AsyncMock(return_value=crawl_result)
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=crawler)
    ctx.__aexit__ = AsyncMock(return_value=False)
    return ctx


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
            return_value=_meta({"title": ""}),
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
            return_value=_meta({"title": ""}),
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
            return_value=_meta({"title": "Page Title"}),
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


@pytest.mark.asyncio
async def test_crawl4ai_maps_text():
    ctx = _crawler_ctx(_crawl_result(True, raw_markdown="page text"))
    with patch("crawl4ai.AsyncWebCrawler", return_value=ctx):
        result = await Crawl4aiProvider().scrape("https://example.com")
    assert result.text == "page text"


@pytest.mark.asyncio
async def test_crawl4ai_captures_title():
    ctx = _crawler_ctx(_crawl_result(True, raw_markdown="text", title="Page Title"))
    with patch("crawl4ai.AsyncWebCrawler", return_value=ctx):
        result = await Crawl4aiProvider().scrape("https://example.com")
    assert result.title == "Page Title"


@pytest.mark.asyncio
async def test_crawl4ai_raises_on_failure():
    cr = _crawl_result(False)
    cr.error_message = "network error"
    ctx = _crawler_ctx(cr)
    with patch("crawl4ai.AsyncWebCrawler", return_value=ctx):
        with pytest.raises(ScrapeError):
            await Crawl4aiProvider().scrape("https://example.com")


@pytest.mark.asyncio
async def test_scrape_router_dispatches_crawl4ai():
    expected = ScrapeResult(url="https://example.com", text="crawl text", title="")
    with patch.object(Crawl4aiProvider, "scrape", new=AsyncMock(return_value=expected)):
        result = await scrape("https://example.com", provider="crawl4ai", settings=Settings())
    assert result == expected
