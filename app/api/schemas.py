"""
Pydantic schemas for API request and response models.
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class GenerateRequest(BaseModel):
    """Request schema for text generation endpoint."""

    prompt: str = Field(..., description="Input prompt for text generation", min_length=1)
    max_tokens: Optional[int] = Field(
        None, 
        description="Maximum number of tokens to generate",
        ge=1,
        le=2048
    )
    temperature: Optional[float] = Field(
        None, 
        description="Sampling temperature (0.0 to 2.0)",
        ge=0.0,
        le=2.0
    )
    top_p: Optional[float] = Field(
        None,
        description="Nucleus sampling parameter",
        ge=0.0,
        le=1.0
    )
    top_k: Optional[int] = Field(
        None,
        description="Top-k sampling parameter",
        ge=1
    )


class GenerateResponse(BaseModel):
    """Response schema for text generation endpoint."""

    generated_text: str = Field(..., description="Generated text output")
    prompt: str = Field(..., description="Original input prompt")
    model: str = Field(..., description="Model used for generation")
    tokens_generated: int = Field(..., description="Number of tokens generated")
    cached: bool = Field(default=False, description="Whether response was served from cache")


class ChatMessage(BaseModel):
    """Schema for a single chat message."""

    role: Literal["system", "user", "assistant"] = Field(
        ..., description="Role of the message sender"
    )
    content: str = Field(..., description="Content of the message", min_length=1)


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""

    messages: List[ChatMessage] = Field(
        ..., description="List of chat messages", min_length=1
    )
    session_id: Optional[str] = Field(
        None, description="Session ID for maintaining chat history across requests"
    )
    max_tokens: Optional[int] = Field(
        None,
        description="Maximum number of tokens to generate",
        ge=1,
        le=2048
    )
    temperature: Optional[float] = Field(
        None,
        description="Sampling temperature (0.0 to 2.0)",
        ge=0.0,
        le=2.0
    )
    stream: bool = Field(default=False, description="Enable streaming responses")

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, messages: List[ChatMessage]) -> List[ChatMessage]:
        """
        Validate chat messages.
        
        Parameters:
            messages (List[ChatMessage]): Messages to validate
            
        Returns:
            List[ChatMessage]: Validated messages
            
        Raises:
            ValueError: If messages are invalid
        """
        if not messages:
            raise ValueError("At least one message is required")
        
        # Last message should be from user
        if messages[-1].role != "user":
            raise ValueError("Last message must be from user")
        
        return messages


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""

    message: ChatMessage = Field(..., description="Assistant's response message")
    model: str = Field(..., description="Model used for generation")
    tokens_generated: int = Field(..., description="Number of tokens generated")
    cached: bool = Field(default=False, description="Whether response was served from cache")


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""

    status: Literal["healthy", "unhealthy"] = Field(..., description="Service health status")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    model_name: str = Field(..., description="Name of the loaded model")


class StatusResponse(BaseModel):
    """Response schema for status endpoint."""

    service_name: str = Field(..., description="Name of the service")
    version: str = Field(..., description="Service version")
    model_name: str = Field(..., description="Name of the loaded model")
    model_device: str = Field(..., description="Device model is running on")
    cache_stats: dict = Field(..., description="Cache statistics")
    rate_limit_enabled: bool = Field(..., description="Whether rate limiting is enabled")


class ErrorResponse(BaseModel):
    """Response schema for error responses."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")
