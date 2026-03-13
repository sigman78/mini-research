import asyncio

from ..config import Settings
from .brave import BraveProvider
from .duckduckgo import DuckDuckGoProvider
from .errors import SearchError
from .models import SearchResult
from .reddit import RedditProvider


async def search(
    query: str,
    max_results: int | None = None,
    provider: str | None = None,
    settings: Settings | None = None,
) -> list[SearchResult]:
    if settings is None:
        settings = Settings()
    resolved_provider = provider or settings.search_provider
    resolved_max = max_results if max_results is not None else settings.search_max_results

    await asyncio.sleep(settings.search_delay_seconds)

    dispatch = {
        "duckduckgo": lambda: DuckDuckGoProvider(),
        "brave": lambda: _get_brave(settings),
        "reddit": lambda: RedditProvider(),
    }

    if resolved_provider not in dispatch:
        raise SearchError(f"unknown provider: {resolved_provider}")

    instance = dispatch[resolved_provider]()
    return await instance.search(query, resolved_max)


def _get_brave(settings: Settings) -> BraveProvider:
    if not settings.brave_api_key:
        raise SearchError("brave_api_key not configured")
    return BraveProvider(api_key=settings.brave_api_key)
