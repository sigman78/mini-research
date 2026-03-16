from .errors import ScrapeError
from .models import ScrapeResult


class Crawl4aiProvider:
    async def scrape(self, url: str) -> ScrapeResult:
        try:
            from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
        except ImportError as e:
            raise ScrapeError("crawl4ai is not installed (pip install crawl4ai)") from e

        browser_config = BrowserConfig(verbose=False)
        run_config = CrawlerRunConfig(verbose=False, log_console=False)
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url, config=run_config)
        if not result.success:
            raise ScrapeError(result.error_message or f"crawl4ai failed: {url}")
        text = result.markdown.raw_markdown if result.markdown else ""
        title = (result.metadata or {}).get("title", "") or ""
        return ScrapeResult(url=url, text=text, title=title)
