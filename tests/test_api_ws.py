"""Test WebSocket API streaming."""
import asyncio
import json

import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket

from app.main import app


@pytest.fixture
def ws_client():
    """Get WebSocket test client."""
    with TestClient(app) as client:
        yield client


async def test_ws_relationship_stream(ws_client):
    """Test relationship lookup streaming."""
    with ws_client.websocket_connect(
        "/relationship/stream",
        headers={"X-API-Key": "dev"}
    ) as ws:
        # Send request
        await ws.send_json({"name": "Saanvi", "trace": True})
        
        # Collect all messages
        messages = []
        try:
            while True:
                msg = await ws.receive_json()
                messages.append(msg)
        except:
            pass
            
        # Verify sequence
        assert any(m["event"] == "start" for m in messages)
        assert any(m["event"] == "graph.node" and m["node"] == "normalize" for m in messages)
        assert any(m["event"] == "graph.node" and m["node"] == "exact_lookup" for m in messages)
        
        # Verify final result
        result = next(m for m in messages if m["event"] == "result")
        assert result["payload"]["person"] == "Saanvi"
        assert result["payload"]["relationship_to_girish"] == "Daughter"
        
        # Verify we got duration
        assert any(m["event"] == "end" and "durationMs" in m for m in messages)