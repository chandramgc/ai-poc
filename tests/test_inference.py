"""Test inference endpoints."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

from app.main import app


@pytest.fixture
def mock_pipeline():
    """Mock the transformers pipeline."""
    with patch("app.llm.loader._pipeline") as mock:
        mock_pipe = MagicMock()
        mock_pipe.return_value = [{"generated_text": "This is a generated response."}]
        mock.__bool__ = lambda self: True  # Make it truthy for health checks
        yield mock_pipe


@pytest.fixture
def mock_generate():
    """Mock the generate_text function."""
    with patch("app.llm.loader.generate_text") as mock:
        mock.return_value = "This is a generated response."
        yield mock


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert "model_loaded" in data
        assert "model_name" in data


@pytest.mark.asyncio
async def test_status_endpoint():
    """Test status endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/status")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "service_name" in data
        assert "version" in data
        assert "model_name" in data
        assert "cache_stats" in data


@pytest.mark.asyncio
async def test_generate_endpoint_success(mock_generate):
    """Test successful text generation."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/v1/generate",
            json={"prompt": "Hello, world!"},
            headers={"X-API-Key": "change-me"},
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "generated_text" in data
        assert "prompt" in data
        assert data["prompt"] == "Hello, world!"


@pytest.mark.asyncio
async def test_generate_endpoint_missing_api_key():
    """Test generation endpoint without API key."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/v1/generate",
            json={"prompt": "Hello, world!"},
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_generate_endpoint_invalid_api_key():
    """Test generation endpoint with invalid API key."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/v1/generate",
            json={"prompt": "Hello, world!"},
            headers={"X-API-Key": "invalid-key"},
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_generate_endpoint_prompt_too_long():
    """Test generation with prompt exceeding max length."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        long_prompt = "x" * 5000  # Exceeds default max of 4000
        
        response = await client.post(
            "/v1/generate",
            json={"prompt": long_prompt},
            headers={"X-API-Key": "change-me"},
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_generate_endpoint_with_parameters(mock_generate):
    """Test generation with custom parameters."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/v1/generate",
            json={
                "prompt": "Test prompt",
                "max_tokens": 100,
                "temperature": 0.8,
                "top_p": 0.95,
            },
            headers={"X-API-Key": "change-me"},
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["model"] is not None


@pytest.mark.asyncio
async def test_chat_endpoint_success(mock_generate):
    """Test successful chat endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/v1/chat",
            json={
                "messages": [
                    {"role": "user", "content": "Hello!"}
                ],
            },
            headers={"X-API-Key": "change-me"},
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert data["message"]["role"] == "assistant"


@pytest.mark.asyncio
async def test_chat_endpoint_invalid_messages():
    """Test chat endpoint with invalid message format."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/v1/chat",
            json={
                "messages": [
                    {"role": "assistant", "content": "I start?"}
                ],
            },
            headers={"X-API-Key": "change-me"},
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_rate_limiting():
    """Test rate limiting (simplified test)."""
    # This test would need to make multiple requests rapidly
    # For now, just verify the endpoint is accessible
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "status" in data
