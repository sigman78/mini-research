import asyncio

from ddgs import DDGS

from .models import SearchResult


class DuckDuckGoProvider:
    name = "duckduckgo"

    def __init__(self, settings=None) -> None:
        pass

    async def search(self, query: str, max_results: int) -> list[SearchResult]:
        raw = await asyncio.to_thread(lambda: list(DDGS().text(query, max_results=max_results)))
        return [
            SearchResult(title=r["title"], url=r["href"], snippet=r.get("body", "")) for r in raw
        ]
