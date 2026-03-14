import pytest

from mini_research.scrape.crawl4ai_provider import Crawl4aiProvider
from mini_research.scrape.jina import JinaProvider
from mini_research.scrape.trafilatura_provider import TrafilaturaProvider

URL = "https://example.com"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_trafilatura_scrapes_example_com():
    result = await TrafilaturaProvider().scrape(URL)
    assert result.url == URL
    assert len(result.text) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_jina_scrapes_example_com():
    result = await JinaProvider().scrape(URL)
    assert result.url == URL
    assert len(result.text) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_crawl4ai_scrapes_example_com():
    result = await Crawl4aiProvider().scrape(URL)
    assert result.url == URL
    assert len(result.text) > 0
