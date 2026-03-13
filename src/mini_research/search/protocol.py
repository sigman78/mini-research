from typing import Protocol

from .models import SearchResult


class SearchProvider(Protocol):
    async def search(self, query: str, max_results: int) -> list[SearchResult]: ...
