"""Test LangGraph workflow."""
import pytest

from app.csv_loader import CsvLoader
from app.graph import RelationshipGraph


@pytest.fixture
def graph():
    """Get test graph instance."""
    loader = CsvLoader("data/relationships.xlsx")
    return RelationshipGraph(loader)


@pytest.mark.asyncio
async def test_graph_exact_match(graph):
    """Test graph workflow with exact match."""
    result = await graph.run("Saanvi")
    
    assert result["person"] == "Saanvi"
    assert result["relationship_to_girish"] == "Daughter"
    assert result["confidence"] == "High"
    assert result["matching"]["strategy"] == "exact"
    assert result["matching"]["score"] == 1.0


@pytest.mark.asyncio
async def test_graph_fuzzy_match(graph):
    """Test graph workflow with fuzzy match."""
    result = await graph.run("Saanvee")
    
    assert result["person"] == "Saanvee"
    assert result["relationship_to_girish"] == "Daughter"
    assert result["confidence"] in ["High", "Medium"]
    assert result["matching"]["strategy"] == "fuzzy"
    assert result["matching"]["score"] >= 0.8


@pytest.mark.asyncio
async def test_graph_streaming(graph):
    """Test graph workflow with streaming."""
    events = []
    async for event in graph.run("Saanvi", stream=True):
        events.append(event)
    
    # Verify event sequence
    assert events[0]["event"] == "start"
    assert any(e["event"] == "graph.node" and e["node"] == "normalize" for e in events)
    assert any(e["event"] == "graph.node" and e["node"] == "exact_lookup" for e in events)
    
    # Verify final result
    result_event = next(e for e in events if e["event"] == "result")
    assert result_event["payload"]["person"] == "Saanvi"
    assert result_event["payload"]["confidence"] == "High"