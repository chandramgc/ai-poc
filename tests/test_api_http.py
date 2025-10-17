"""Test HTTP API endpoints."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Get test client."""
    return TestClient(app)


@pytest.fixture
def api_headers():
    """Get API headers with key."""
    return {"X-API-Key": "dev"}


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_relationship_exact(client, api_headers):
    """Test relationship lookup with exact match."""
    response = client.get("/relationship?name=Saanvi", headers=api_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["person"] == "Saanvi"
    assert data["relationship_to_girish"] == "Daughter"
    assert data["confidence"] == "High"
    assert data["matching"]["strategy"] == "exact"


def test_get_relationship_fuzzy(client, api_headers):
    """Test relationship lookup with fuzzy match."""
    response = client.get("/relationship?name=Saanvee", headers=api_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["person"] == "Saanvee"
    assert data["relationship_to_girish"] == "Daughter"
    assert data["confidence"] in ["High", "Medium"]
    assert data["matching"]["strategy"] == "fuzzy"


def test_get_relationship_not_found(client, api_headers):
    """Test relationship lookup with unknown name."""
    response = client.get("/relationship?name=Unknown", headers=api_headers)
    assert response.status_code == 404
    assert "error" in response.json()


def test_get_relationship_unauthorized(client):
    """Test relationship lookup without API key."""
    response = client.get("/relationship?name=Saanvi")
    assert response.status_code == 401


def test_reload_data(client, api_headers):
    """Test data reload endpoint."""
    response = client.post("/reload", headers=api_headers)
    assert response.status_code == 204