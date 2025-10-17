"""Pydantic models for the Relationship Finder MCP service."""
from datetime import datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ConfidenceLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class MatchingInfo(BaseModel):
    strategy: Literal["exact", "fuzzy"] = Field(..., description="The matching strategy used")
    score: float = Field(..., description="Matching score between 0 and 1")


class SourceInfo(BaseModel):
    file: str = Field(..., description="Source Excel file name")
    last_loaded_at: datetime = Field(..., description="When the data was last loaded")
    rows: int = Field(..., description="Total number of rows in the dataset")


class RelationshipResponse(BaseModel):
    person: str = Field(..., description="Normalized person name")
    relationship_to_girish: str = Field(..., description="Relationship to Girish")
    confidence: ConfidenceLevel = Field(..., description="Confidence level of the match")
    matching: MatchingInfo = Field(..., description="Details about the matching process")
    source: SourceInfo = Field(..., description="Information about the data source")


class WSRequest(BaseModel):
    name: str = Field(..., description="Name to look up")
    trace: bool = Field(False, description="Whether to include trace events")


class ErrorResponse(BaseModel):
    error: dict[str, str] = Field(
        ..., description="Error details with code, message, and trace ID"
    )