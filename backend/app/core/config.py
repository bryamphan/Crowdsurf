"""App settings, loaded from environment variables (or a .env file).

Use get_settings() anywhere you need a setting, e.g. get_settings().room_ttl_hours.
Never hardcode secrets or URLs in the code.

What's left to do:
- When you need a new setting, add it to the Settings class below with a default,
  and add it to .env.example at the root of the repo so teammates know it exists.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings, read from environment variables (and .env if present)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://crowdsurf:crowdsurf@localhost:5432/crowdsurf"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "change-me"

    room_ttl_hours: int = 12
    vote_rate_limit: int = 10
    search_cache_ttl: int = 3600

    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
