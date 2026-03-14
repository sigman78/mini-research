from mini_research.config import Settings
from mini_research.scrape import ScrapeError, scrape
from mini_research.search import search
from mini_research.state import Fact


async def search_tool(query: str, settings: Settings | None = None) -> list:
    return await search(query, settings=settings)


async def extract_tool(url: str, settings: Settings | None = None) -> Fact | None:
    try:
        result = await scrape(url, settings=settings)
    except ScrapeError:
        return None
    if not result.text.strip():
        return None
    return Fact(text=result.text[:4000], source_url=url, source_title=result.title)
