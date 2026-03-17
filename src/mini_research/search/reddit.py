from .models import SearchResult


class RedditProvider:
    name = "reddit"

    def __init__(self, settings=None) -> None:
        pass

    async def search(self, query: str, max_results: int) -> list[SearchResult]:
        raise NotImplementedError("Reddit search not implemented")
