import httpx

from ..config import Settings
from .errors import SearchError
from .models import SearchResult


class BraveProvider:
    name = "brave"

    def __init__(self, settings: Settings | None = None) -> None:
        if not settings or not settings.brave_api_key:
            raise SearchError("brave_api_key not configured")
        self._api_key = settings.brave_api_key

    async def search(self, query: str, max_results: int) -> list[SearchResult]:
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self._api_key,
        }
        params = {"q": query, "count": max_results}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    headers=headers,
                    params=params,
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise SearchError(str(exc)) from exc
        results = response.json().get("web", {}).get("results", [])
        return [
            SearchResult(title=r["title"], url=r["url"], snippet=r.get("description", ""))
            for r in results
        ]
