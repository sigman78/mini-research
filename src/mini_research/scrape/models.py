from pydantic import BaseModel


class ScrapeResult(BaseModel):
    url: str
    text: str
    title: str = ""
