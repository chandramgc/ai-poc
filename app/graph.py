"""LangGraph workflow for the Relationship Finder MCP service."""
from typing import Any, AsyncIterator, Dict, Optional, Union

from langgraph.graph import Graph, StateGraph

from app.excel_loader import ExcelLoader
from app.match import confidence_from_score, exact_lookup, fuzzy_lookup, normalize
from app.schemas import ConfidenceLevel


class RelationshipGraph:
    """LangGraph-based relationship lookup workflow."""

    def __init__(self, excel_loader: ExcelLoader):
        """Initialize the graph with data loader."""
        self.excel_loader = excel_loader
        self.graph = self._build_graph()

    def _normalize_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize input name and validate."""
        name = state.get("name", "")
        if not name.strip():
            return {"error": "Name cannot be empty"}
            
        state["normalized_name"] = normalize(name)
        return state

    def _exact_lookup_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt exact lookup."""
        df = self.excel_loader.get_df()
        result = exact_lookup(df, state["normalized_name"])
        
        if result is not None:
            state["match"] = {
                "row": result,
                "strategy": "exact",
                "score": 1.0,
            }
        return state

    def _fuzzy_lookup_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt fuzzy lookup if exact match fails."""
        from app.config import get_settings
        
        if not get_settings().ALLOW_FUZZY:
            return state
            
        df = self.excel_loader.get_df()
        row, score = fuzzy_lookup(df, state["normalized_name"])
        
        if row is not None:
            state["match"] = {
                "row": row,
                "strategy": "fuzzy",
                "score": score,
            }
        return state

    def _compose_result_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Compose final response based on best match."""
        match = state.get("match")
        if not match:
            state["result"] = {
                "person": "Unknown",
                "relationship_to_girish": "Unknown",
                "confidence": ConfidenceLevel.LOW,
                "matching": {"strategy": "none", "score": 0.0},
                "source": {
                    "file": self.excel_loader.excel_path,
                    "last_loaded_at": self.excel_loader.get_last_loaded(),
                    "rows": self.excel_loader.get_row_count(),
                }
            }
            return state
            
        row = match["row"]
        score = match["score"]
        
        state["result"] = {
            "person": row["Name"],
            "relationship_to_girish": row["RelationshipToGirish"],
            "confidence": confidence_from_score(score),
            "matching": {
                "strategy": match["strategy"],
                "score": score,
            },
            "source": {
                "file": self.excel_loader.excel_path,
                "last_loaded_at": self.excel_loader.get_last_loaded(),
                "rows": self.excel_loader.get_row_count(),
            }
        }
        return state

    def _should_try_fuzzy(self, state: Dict[str, Any]) -> bool:
        """Determine if fuzzy search should be attempted."""
        return "match" not in state

    def _build_graph(self) -> Graph:
        """Build the LangGraph workflow."""
        workflow = StateGraph()

        # Add nodes
        workflow.add_node("normalize", self._normalize_node)
        workflow.add_node("exact_lookup", self._exact_lookup_node)
        workflow.add_node("fuzzy_lookup", self._fuzzy_lookup_node)
        workflow.add_node("compose_result", self._compose_result_node)

        # Add edges
        workflow.add_edge("normalize", "exact_lookup")
        workflow.add_conditional_edges(
            "exact_lookup",
            self._should_try_fuzzy,
            {
                True: "fuzzy_lookup",
                False: "compose_result"
            }
        )
        workflow.add_edge("fuzzy_lookup", "compose_result")

        # Set entry and exit
        workflow.set_entry_point("normalize")
        workflow.set_finish_point("compose_result")

        return workflow.compile()

    async def run(self, name: str, stream: bool = False) -> Union[Dict[str, Any], AsyncIterator[Dict[str, Any]]]:
        """Run the relationship lookup workflow."""
        state = {"name": name}
        
        if not stream:
            final_state = await self.graph.arun(state)
            return final_state["result"]
            
        async for event in self.graph.astream(state):
            if event["event"] == "start":
                yield {"event": "start", "name": name}
            elif event["event"] == "node":
                yield {
                    "event": "graph.node",
                    "node": event["node"],
                    **({"result": event["data"]["result"]} if "result" in event["data"] else {})
                }
            elif event["event"] == "end":
                yield {
                    "event": "result",
                    "payload": event["data"]["result"]
                }
                yield {
                    "event": "end",
                    "durationMs": int(event["duration"] * 1000)
                }