from typing import Protocol

from .models import ScrapeResult


class ScrapeProvider(Protocol):
    async def scrape(self, url: str) -> ScrapeResult: ...
