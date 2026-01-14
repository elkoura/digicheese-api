from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Digicheese API"
    api_prefix: str = "/api"
    debug: bool = False

    # Database
    database_url: AnyUrl = Field(
        default="postgresql+psycopg://digicheese:digicheese@localhost:5433/digicheese"
    )

    # Auth / JWT
    # Default value is long enough to satisfy validation but MUST be overridden in production.
    jwt_secret_key: str = Field(default="CHANGE_ME_IN_LOCAL_DEV_ONLY", min_length=16)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30

    # CORS
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    # Operational
    log_level: str = "INFO"
    auto_create_tables: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()

