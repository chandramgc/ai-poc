"""Main service module for the Relationship Finder MCP service."""
from typing import AsyncIterator, Dict, Optional, Union

from app.config import get_settings
from app.csv_loader import CsvLoader
from app.graph import RelationshipGraph


class RelationshipService:
    """Main service class coordinating data loading and relationship lookup."""

    def __init__(self):
        """Initialize service with Excel loader and graph."""
        settings = get_settings()
        self.excel_loader = CsvLoader(
            settings.EXCEL_PATH,
            settings.ALIASES_PATH
        )
        self.graph = RelationshipGraph(self.excel_loader)

    async def get_relationship(
        self, name: str, stream: bool = False
    ) -> Union[Dict[str, any], AsyncIterator[Dict[str, any]]]:
        """Look up a relationship using the graph workflow."""
        if stream:
            # Return the async iterator directly
            return self.graph.run_stream(name)
        else:
            return await self.graph.run(name, stream)

    def get_relationship_stream(self, name: str):
        """Get relationship lookup as a streaming async iterator."""
        return self.graph.run_stream(name)

    def reload_data(self) -> None:
        """Force reload of Excel data."""
        self.excel_loader.reload()

    def get_health(self) -> Dict[str, any]:
        """Get service health information."""
        return {
            "status": "ok",
            "version": "0.1.0",
            "data": {
                "last_loaded": self.excel_loader.get_last_loaded(),
                "row_count": self.excel_loader.get_row_count(),
            }
        }