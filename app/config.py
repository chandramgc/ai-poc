"""Configuration settings for the Relationship Finder MCP service."""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # Server settings
    PORT: int = 8000
    LOG_LEVEL: str = "DEBUG"
    API_KEY: str = "dev"
    CORS_ORIGINS: str = "http://localhost:3000"

    # Feature flags
    ALLOW_FUZZY: bool = True

    # Data settings
    EXCEL_PATH: str = "data/relationships.csv"
    ALIASES_PATH: Optional[str] = None

    # Redis settings (optional)
    REDIS_URL: Optional[str] = None

    # Matching thresholds
    HIGH_CONFIDENCE_THRESHOLD: float = 0.95
    MEDIUM_CONFIDENCE_THRESHOLD: float = 0.80


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()