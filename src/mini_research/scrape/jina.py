import httpx

from .errors import ScrapeError
from .models import ScrapeResult

JINA_BASE = "https://r.jina.ai"


class JinaProvider:
    async def scrape(self, url: str) -> ScrapeResult:
        jina_url = f"{JINA_BASE}/{url}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(jina_url, headers={"Accept": "text/plain"})
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise ScrapeError(str(exc)) from exc
        return ScrapeResult(url=url, text=response.text, title="")
