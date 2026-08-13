from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Enterprise Agentic RAG API"
    app_env: str = "development"

    database_url: str = ""

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    phoenix_enabled: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()

    if not settings.database_url:
        raise RuntimeError(
            "DATABASE_URL is not configured"
        )

    if settings.database_url.startswith(
        "postgres://"
    ):
        settings.database_url = settings.database_url.replace(
            "postgres://",
            "postgresql+asyncpg://",
            1,
        )

    elif settings.database_url.startswith(
        "postgresql://"
    ):
        settings.database_url = settings.database_url.replace(
            "postgresql://",
            "postgresql+asyncpg://",
            1,
        )

    return settings


settings = get_settings()