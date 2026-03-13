import asyncio

from duckduckgo_search import DDGS

from .models import SearchResult


class DuckDuckGoProvider:
    async def search(self, query: str, max_results: int) -> list[SearchResult]:
        raw = await asyncio.to_thread(lambda: list(DDGS().text(query, max_results=max_results)))
        return [
            SearchResult(title=r["title"], url=r["href"], snippet=r.get("body", "")) for r in raw
        ]
