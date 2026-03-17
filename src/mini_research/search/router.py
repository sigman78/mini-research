import asyncio
import functools

from ..config import Settings
from .brave import BraveProvider
from .duckduckgo import DuckDuckGoProvider
from .errors import SearchError
from .models import SearchResult
from .reddit import RedditProvider

_PROVIDERS = [DuckDuckGoProvider, BraveProvider, RedditProvider]


@functools.cache
def _registry() -> dict[str, type]:
    return {cls.name: cls for cls in _PROVIDERS}


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

    registry = _registry()
    if resolved_provider not in registry:
        raise SearchError(f"unknown provider: {resolved_provider}")

    instance = registry[resolved_provider](settings)
    return await instance.search(query, resolved_max)
