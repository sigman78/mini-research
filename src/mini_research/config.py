from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    brave_api_key: str | None = None
    reddit_client_id: str | None = None
    reddit_client_secret: str | None = None
    litellm_model: str = "openai/gpt-4o-mini"

    model_config = {"env_file": ".env", "extra": "ignore"}
