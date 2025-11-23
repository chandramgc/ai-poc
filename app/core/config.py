"""
Core configuration module for the medicine news scraper.

Handles environment variable loading and validation using pydantic-settings.
"""
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Attributes:
        app_name: Application name
        debug: Debug mode flag
        max_results: Maximum number of search results to return
        user_agent: User agent string for HTTP requests
        request_timeout: HTTP request timeout in seconds
        request_delay: Delay between requests in seconds (rate limiting)
        scraper_backend: Backend to use for scraping (bs4, scrapy, or playwright)
        cache_ttl: Cache time-to-live in seconds
        cache_max_size: Maximum number of items in cache
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application settings
    app_name: str = "Medicine News Scraper"
    debug: bool = False
    
    # Scraping settings
    max_results: int = 10
    user_agent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    request_timeout: int = 30  # Increased timeout for slow responses
    request_delay: float = 0.5  # Reduced initial delay for better UX
    
    # Test mode - returns mock data without making real requests
    test_mode: bool = False
    
    # Backend selection
    scraper_backend: Literal["bs4", "scrapy", "playwright"] = "bs4"
    
    # Cache settings
    cache_ttl: int = 3600  # 1 hour
    cache_max_size: int = 100
    
    # Retry settings
    max_retries: int = 3
    retry_backoff_factor: float = 2.0  # Exponential backoff multiplier
    
    def validate_backend(self) -> None:
        """Validate that the selected backend is supported."""
        valid_backends = ["bs4", "scrapy", "playwright"]
        if self.scraper_backend not in valid_backends:
            raise ValueError(
                f"Invalid SCRAPER_BACKEND: {self.scraper_backend}. "
                f"Must be one of {valid_backends}"
            )


# Global settings instance
settings = Settings()

# Validate backend on startup
settings.validate_backend()
