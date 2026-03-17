import functools

from ..config import Settings
from .crawl4ai_provider import Crawl4aiProvider
from .errors import ScrapeError
from .jina import JinaProvider
from .models import ScrapeResult
from .trafilatura_provider import TrafilaturaProvider

_PROVIDERS = [TrafilaturaProvider, JinaProvider, Crawl4aiProvider]


@functools.cache
def _registry() -> dict[str, type]:
    return {cls.name: cls for cls in _PROVIDERS}


async def scrape(
    url: str,
    provider: str | None = None,
    settings: Settings | None = None,
) -> ScrapeResult:
    if settings is None:
        settings = Settings()
    resolved_provider = provider or settings.scrape_provider

    registry = _registry()
    if resolved_provider not in registry:
        raise ScrapeError(f"unknown provider: {resolved_provider}")

    instance = registry[resolved_provider]()
    return await instance.scrape(url)
