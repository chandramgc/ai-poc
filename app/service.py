"""Main service module for the Relationship Finder MCP service."""
from typing import AsyncIterator, Dict, Optional, Union

from app.config import get_settings
from app.excel_loader import ExcelLoader
from app.graph import RelationshipGraph


class RelationshipService:
    """Main service class coordinating data loading and relationship lookup."""

    def __init__(self):
        """Initialize service with Excel loader and graph."""
        settings = get_settings()
        self.excel_loader = ExcelLoader(
            settings.EXCEL_PATH,
            settings.ALIASES_PATH
        )
        self.graph = RelationshipGraph(self.excel_loader)

    async def get_relationship(
        self, name: str, stream: bool = False
    ) -> Union[Dict[str, any], AsyncIterator[Dict[str, any]]]:
        """Look up a relationship using the graph workflow."""
        return await self.graph.run(name, stream)

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