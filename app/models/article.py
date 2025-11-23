"""
Pydantic models for article data representation.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class Article(BaseModel):
    """
    Article model representing a search result.
    
    Attributes:
        title: Article title
        url: Article URL
        snippet: Brief description/snippet from the search result
        source: Source website or publication name
        published_date: Publication date (optional, may not always be available)
    """
    
    title: str = Field(..., description="Article title")
    url: HttpUrl = Field(..., description="Article URL")
    snippet: str = Field(..., description="Article snippet or description")
    source: Optional[str] = Field(None, description="Source website or publication")
    published_date: Optional[str] = Field(
        None,
        description="Publication date (human-readable string from Google)"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "New Insulin Treatment Shows Promise",
                    "url": "https://example.com/insulin-treatment",
                    "snippet": "Researchers have developed a new insulin formulation...",
                    "source": "Medical News Today",
                    "published_date": "2 days ago"
                }
            ]
        }
    }


class SearchResponse(BaseModel):
    """
    Response model for search endpoint.
    
    Attributes:
        query: The search query used
        results: List of article results
        count: Number of results returned
        cached: Whether results were served from cache
    """
    
    query: str = Field(..., description="Search query")
    results: list[Article] = Field(..., description="List of article results")
    count: int = Field(..., description="Number of results returned")
    cached: bool = Field(False, description="Whether results were served from cache")


class ErrorResponse(BaseModel):
    """
    Error response model.
    
    Attributes:
        error: Error type
        message: Error message
        details: Additional error details (optional)
    """
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")
