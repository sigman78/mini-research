from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    brave_api_key: str | None = None
    reddit_client_id: str | None = None
    reddit_client_secret: str | None = None
    litellm_model: str = "openai/gpt-4o-mini"
    search_provider: str = "duckduckgo"
    scrape_provider: str = "trafilatura"
    search_max_results: int = 5
    search_delay_seconds: float = 0.5

    model_config = {"env_file": ".env", "extra": "ignore"}
