"""Test configuration loading and merging."""

import os
from unittest.mock import patch

import pytest

from app.core.config import get_settings


def test_config_loads_defaults():
    """Test that configuration loads with default values."""
    settings = get_settings()
    
    assert settings.app.name == "LLM FastAPI Service"
    assert settings.app.port == 8000
    assert settings.model.name is not None


def test_config_env_override():
    """Test that environment variables override YAML config."""
    with patch.dict(os.environ, {"MODEL__MAX_TOKENS": "1024", "APP__PORT": "9000"}):
        # Clear cache to reload settings
        get_settings.cache_clear()
        settings = get_settings()
        
        assert settings.model.max_tokens == 1024
        assert settings.app.port == 9000


def test_security_config():
    """Test security configuration."""
    settings = get_settings()
    
    assert settings.security.max_prompt_chars > 0
    assert isinstance(settings.security.enable_pii_filter, bool)


def test_rate_limit_config():
    """Test rate limit configuration."""
    settings = get_settings()
    
    assert settings.rate_limit.requests_per_minute > 0
    assert settings.rate_limit.burst_size > 0


def test_cache_config():
    """Test cache configuration."""
    settings = get_settings()
    
    assert settings.cache.size > 0
    assert settings.cache.ttl_seconds > 0


def test_model_config():
    """Test model configuration."""
    settings = get_settings()
    
    assert settings.model.name is not None
    assert settings.model.source in ["hub", "local"]
    assert settings.model.device in ["cpu", "cuda"]
    assert 0.0 <= settings.model.temperature <= 2.0
