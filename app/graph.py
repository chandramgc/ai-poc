"""LangGraph workflow for the Relationship Finder MCP service."""
import logging
from typing import Any, AsyncIterator, Dict, Optional, Union, List

from langgraph.graph.state import StateGraph
from pydantic import BaseModel

from app.csv_loader import CsvLoader
from app.match import confidence_from_score, exact_lookup, fuzzy_lookup, normalize
from app.schemas import ConfidenceLevel

logger = logging.getLogger(__name__)


class GraphState(BaseModel):
    """State model for the relationship graph."""
    name: str
    normalized_name: Optional[str] = None
    exact_match: Optional[Dict[str, Any]] = None
    fuzzy_matches: Optional[List[Dict[str, Any]]] = None
    result: Optional[Dict[str, Any]] = None
    next: Optional[str] = None


class RelationshipGraph:
    """LangGraph-based relationship lookup workflow."""

    def __init__(self, excel_loader: CsvLoader):
        """Initialize the graph with data loader."""
        self.excel_loader = excel_loader
        self.graph = self._build_graph()
        logger.info("Initialized RelationshipGraph")

    def _build_graph(self) -> StateGraph:
        """Build the workflow graph."""
        # Create graph with state schema
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("normalize", self._normalize_node)
        workflow.add_node("exact_lookup", self._exact_lookup_node)
        workflow.add_node("fuzzy_lookup", self._fuzzy_lookup_node)

        # Define edges
        from langgraph.graph import START, END
        
        # Start with normalize
        workflow.add_edge(START, "normalize")
        
        # Always go to exact lookup after normalize
        workflow.add_edge("normalize", "exact_lookup")
        
        # Go to fuzzy lookup only if exact lookup doesn't find a match
        workflow.add_conditional_edges(
            "exact_lookup",
            lambda x: "fuzzy_lookup" if getattr(x, "next", None) == "fuzzy_lookup" else END
        )
        
        # After fuzzy lookup, always end
        workflow.add_edge("fuzzy_lookup", END)
        
        # Set entry and finish points
        workflow.set_entry_point("normalize")
        
        logger.debug("Built workflow graph with nodes: normalize -> exact_lookup -> fuzzy_lookup")
        return workflow.compile()

    def _get_source_info(self) -> dict:
        """Get source information from the CSV loader."""
        return {
            "file": "data/relationships.xlsx",
            "last_loaded_at": self.excel_loader.get_last_loaded().isoformat(),
            "rows": self.excel_loader.get_row_count()
        }

    def _normalize_node(self, state: GraphState) -> GraphState:
        """Normalize the input name."""
        name = state.name
        normalized = normalize(name)
        logger.info(f"Input name: {name}")
        logger.debug(f"Normalized name: {normalized}")
        
        # Log DataFrame info for debugging
        df = self.excel_loader.data
        logger.debug(f"DataFrame columns: {df.columns.tolist()}")
        logger.debug(f"Sample data:\n{df[['Name', 'RelationshipToGirish']].head()}")
        
        return GraphState(
            name=name,
            normalized_name=normalized,
            next="exact_lookup"
        )
    
    def _exact_lookup_node(self, state: GraphState) -> GraphState:
        """Look up the exact match for the normalized name."""
        normalized_name = state.normalized_name
        df = self.excel_loader.data
        
        logger.debug(f"Looking for exact match of '{normalized_name}' in DataFrame")
        exact_match = exact_lookup(df, normalized_name)
        
        if exact_match is not None:
            logger.info(f"Found exact match: {dict(exact_match)}")
            match_dict = dict(exact_match)
            return GraphState(
                name=state.name,
                normalized_name=state.normalized_name,
                exact_match=match_dict,
                result={
                    "person": match_dict["Name"],
                    "relationship_to_girish": match_dict["RelationshipToGirish"],
                    "confidence": ConfidenceLevel.HIGH.value,
                    "matching": {
                        "strategy": "exact",
                        "score": 1.0
                    },
                    "source": self._get_source_info()
                }
            )
        
        logger.info("No exact match found, trying fuzzy lookup")
        return GraphState(
            name=state.name,
            normalized_name=state.normalized_name,
            exact_match=state.exact_match,
            fuzzy_matches=state.fuzzy_matches,
            next="fuzzy_lookup"
        )

    def _fuzzy_lookup_node(self, state: GraphState) -> GraphState:
        """Look up fuzzy matches for the normalized name."""
        normalized_name = state.normalized_name
        match, score = fuzzy_lookup(self.excel_loader.data, normalized_name)
        
        # Get best match if available
        if match is not None and score > 0:
            logger.info(f"Found fuzzy match: {dict(match)} with score {score}")
            match_dict = dict(match)
            confidence = confidence_from_score(score)
            
            return GraphState(
                name=state.name,
                normalized_name=state.normalized_name,
                fuzzy_matches=[{
                    "name": match_dict["Name"],
                    "relationship": match_dict["RelationshipToGirish"],
                    "score": score
                }],
                result={
                    "person": match_dict["Name"],
                    "relationship_to_girish": match_dict["RelationshipToGirish"],
                    "confidence": confidence.value,
                    "matching": {
                        "strategy": "fuzzy",
                        "score": score
                    },
                    "source": self._get_source_info()
                }
            )
        
        # No matches found
        logger.info("No fuzzy matches found")
        return GraphState(
            name=state.name,
            normalized_name=state.normalized_name,
            result={
                "person": state.name,
                "relationship_to_girish": "Unknown",
                "confidence": ConfidenceLevel.LOW.value,
                "matching": {
                    "strategy": "fuzzy",
                    "score": 0.0
                },
                "source": self._get_source_info()
            }
        )

    async def run_stream(self, name: str) -> AsyncIterator[Dict[str, Any]]:
        """Run the relationship lookup workflow in streaming mode."""
        try:
            logger.info(f"Starting streaming workflow for name: {name}")
            # Start event
            yield {"event": "start", "name": name}
            
            # Initialize state as GraphState
            current_state = GraphState(name=name)
            current_node = "normalize"
            
            while current_node:
                logger.debug(f"Processing node: {current_node}")
                yield {"event": "node", "node": current_node}
                
                # Get the node function
                node_func = getattr(self, f"_{current_node}_node")
                
                # Execute node
                try:
                    result = node_func(current_state)
                    current_state = result
                    
                    # Yield result if available
                    if current_state.result:
                        logger.info("Found result, yielding response")
                        yield {
                            "event": "result", 
                            "payload": current_state.result
                        }
                    
                    # Get next node
                    current_node = current_state.next
                    
                except Exception as e:
                    logger.error(f"Error in node {current_node}: {str(e)}", exc_info=True)
                    yield {"event": "error", "error": str(e)}
                    break
                    
        except Exception as e:
            logger.error(f"Error in streaming workflow: {str(e)}", exc_info=True)
            yield {"event": "error", "error": str(e)}

    async def run(self, name: str, stream: bool = False) -> Union[Dict[str, Any], AsyncIterator[Dict[str, Any]]]:
        """Run the relationship lookup workflow."""
        if stream:
            return self.run_stream(name)

        # For non-streaming mode, run through graph
        try:
            logger.info(f"Starting sync workflow for name: {name}")
            initial_state = GraphState(name=name)
            
            # Start graph execution with initial state
            logger.debug("Starting graph execution")
            try:
                # Run the graph using StateGraph API
                final_outputs = await self.graph.ainvoke(initial_state.dict())
                logger.debug(f"Final outputs: {final_outputs}")
                
                # Extract result from final outputs if available
                if isinstance(final_outputs, dict) and "result" in final_outputs:
                    logger.info("Found result in outputs")
                    return final_outputs["result"]
                
            except Exception as e:
                logger.error(f"Error running graph: {str(e)}", exc_info=True)
                raise
                
            # If we get here, no result was found
            logger.warning("No result found, returning unknown response")
            return {
                "person": name,
                "relationship_to_girish": "Unknown",
                "confidence": ConfidenceLevel.LOW.value,
                "matching": {
                    "strategy": "fuzzy",
                    "score": 0.0
                },
                "source": self._get_source_info()
            }
            
        except Exception as e:
            logger.error(f"Error in sync workflow: {str(e)}", exc_info=True)
            return {
                "person": name,
                "relationship_to_girish": "Unknown",
                "confidence": ConfidenceLevel.LOW.value,
                "matching": {
                    "strategy": "error",
                    "score": 0.0,
                    "error": str(e)
                },
                "source": self._get_source_info()
            }