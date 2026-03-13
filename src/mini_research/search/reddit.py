from .models import SearchResult


class RedditProvider:
    async def search(self, query: str, max_results: int) -> list[SearchResult]:
        raise NotImplementedError("Reddit search not implemented")
