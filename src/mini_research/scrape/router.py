from ..config import Settings
from .errors import ScrapeError
from .jina import JinaProvider
from .models import ScrapeResult
from .trafilatura_provider import TrafilaturaProvider


async def scrape(
    url: str,
    provider: str | None = None,
    settings: Settings | None = None,
) -> ScrapeResult:
    if settings is None:
        settings = Settings()
    resolved_provider = provider or settings.scrape_provider

    dispatch = {
        "trafilatura": TrafilaturaProvider,
        "jina": JinaProvider,
    }

    if resolved_provider not in dispatch:
        raise ScrapeError(f"unknown provider: {resolved_provider}")

    instance = dispatch[resolved_provider]()
    return await instance.scrape(url)
