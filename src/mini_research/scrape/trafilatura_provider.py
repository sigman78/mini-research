import asyncio

import trafilatura

from .models import ScrapeResult


class TrafilaturaProvider:
    async def scrape(self, url: str) -> ScrapeResult:
        html = await asyncio.to_thread(trafilatura.fetch_url, url)
        text = ""
        title = ""
        if html:
            text = await asyncio.to_thread(trafilatura.extract, html) or ""
            meta = await asyncio.to_thread(trafilatura.bare_extraction, html)
            if meta:
                title = meta.as_dict().get("title", "") or ""
        return ScrapeResult(url=url, text=text, title=title)
