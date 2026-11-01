from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database: PostgreSQL in Docker, SQLite fallback for quick local runs/tests
    database_url: str = "sqlite:///./app.db"

    # JWT auth
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # AI integration (optional). If no key is set, a local fallback summarizer is used.
    anthropic_api_key: str = ""
    ai_model: str = "claude-sonnet-5-5"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
