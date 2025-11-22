"""
Core configuration module using Pydantic Settings.

Loads configuration from config.yml and .env files with .env taking precedence.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

import yaml
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Load .env file first
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class AppConfig(BaseSettings):
    """Application configuration settings."""

    name: str = Field(default="LLM FastAPI Service")
    version: str = Field(default="0.1.0")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    log_level: str = Field(default="INFO")

    model_config = SettingsConfigDict(env_prefix="APP__", case_sensitive=False)


class ModelConfig(BaseSettings):
    """Model configuration settings."""

    name: str = Field(default="google/gemma-2-2b-it")
    source: Literal["hub", "local"] = Field(default="hub")
    device: Literal["cpu", "cuda"] = Field(default="cpu")
    max_tokens: int = Field(default=512)
    temperature: float = Field(default=0.7)
    top_p: float = Field(default=0.9)
    top_k: int = Field(default=50)

    model_config = SettingsConfigDict(env_prefix="MODEL__", case_sensitive=False)


class SecurityConfig(BaseSettings):
    """Security configuration settings."""

    api_key: str = Field(default="change-me")
    max_prompt_chars: int = Field(default=4000)
    enable_pii_filter: bool = Field(default=False)

    model_config = SettingsConfigDict(env_prefix="SECURITY__", case_sensitive=False)


class RateLimitConfig(BaseSettings):
    """Rate limiting configuration settings."""

    enabled: bool = Field(default=True)
    requests_per_minute: int = Field(default=10)
    burst_size: int = Field(default=15)

    model_config = SettingsConfigDict(env_prefix="RATE_LIMIT__", case_sensitive=False)


class CacheConfig(BaseSettings):
    """Cache configuration settings."""

    enabled: bool = Field(default=True)
    size: int = Field(default=100)
    ttl_seconds: int = Field(default=3600)

    model_config = SettingsConfigDict(env_prefix="CACHE__", case_sensitive=False)


class ChatHistoryConfig(BaseSettings):
    """Chat history configuration settings."""

    enabled: bool = Field(default=True)
    ttl_seconds: int = Field(default=7200)  # 2 hours default

    model_config = SettingsConfigDict(env_prefix="CHAT_HISTORY__", case_sensitive=False)


class MetricsConfig(BaseSettings):
    """Metrics configuration settings."""

    enabled: bool = Field(default=True)
    endpoint: str = Field(default="/metrics")

    model_config = SettingsConfigDict(env_prefix="METRICS__", case_sensitive=False)


class LoggingConfig(BaseSettings):
    """Logging configuration settings."""

    format: Literal["json", "text"] = Field(default="json")
    level: str = Field(default="INFO")
    include_request_body: bool = Field(default=False)

    model_config = SettingsConfigDict(env_prefix="LOGGING__", case_sensitive=False)


class Settings(BaseSettings):
    """Main settings class combining all configuration sections."""

    app: AppConfig = Field(default_factory=AppConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    chat_history: ChatHistoryConfig = Field(default_factory=ChatHistoryConfig)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    # Hugging Face token from environment
    huggingface_token: Optional[str] = Field(default=None, alias="HUGGINGFACE_TOKEN")

    model_config = SettingsConfigDict(case_sensitive=False, extra="allow")


def load_yaml_config(config_path: str = "config.yml") -> dict:
    """
    Load configuration from YAML file.
    
    Parameters:
        config_path (str): Path to the YAML configuration file
        
    Returns:
        dict: Configuration dictionary
    """
    config_file = Path(__file__).parent.parent.parent / config_path
    
    if not config_file.exists():
        return {}
    
    with open(config_file, "r") as f:
        return yaml.safe_load(f) or {}


def merge_configs(yaml_config: dict) -> Settings:
    """
    Merge YAML configuration with environment variables.
    
    Environment variables take precedence over YAML config.
    
    Parameters:
        yaml_config (dict): Configuration from YAML file
        
    Returns:
        Settings: Merged configuration settings
    """
    # Initialize each config section
    app_config = AppConfig(**yaml_config.get("app", {}))
    model_config = ModelConfig(**yaml_config.get("model", {}))
    security_config = SecurityConfig(**yaml_config.get("security", {}))
    rate_limit_config = RateLimitConfig(**yaml_config.get("rate_limit", {}))
    cache_config = CacheConfig(**yaml_config.get("cache", {}))
    chat_history_config = ChatHistoryConfig(**yaml_config.get("chat_history", {}))
    metrics_config = MetricsConfig(**yaml_config.get("metrics", {}))
    logging_config = LoggingConfig(**yaml_config.get("logging", {}))
    
    # Get Hugging Face token from environment
    huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
    
    return Settings(
        app=app_config,
        model=model_config,
        security=security_config,
        rate_limit=rate_limit_config,
        cache=cache_config,
        chat_history=chat_history_config,
        metrics=metrics_config,
        logging=logging_config,
        huggingface_token=huggingface_token,
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Loads configuration from YAML and merges with environment variables.
    Uses LRU cache to ensure singleton behavior.
    
    Returns:
        Settings: Application settings
    """
    yaml_config = load_yaml_config()
    return merge_configs(yaml_config)


# Convenience function for quick access
settings = get_settings()
