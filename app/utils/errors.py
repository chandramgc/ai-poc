"""Utility classes and functions for error handling."""

from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


class ServiceError(Exception):
    """Base exception for service errors."""

    def __init__(
        self, 
        message: str, 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize service error.
        
        Parameters:
            message (str): Error message
            status_code (int): HTTP status code
            details (Optional[Dict[str, Any]]): Additional error details
        """
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ModelLoadError(ServiceError):
    """Exception raised when model fails to load."""

    def __init__(self, message: str = "Failed to load model", details: Optional[Dict] = None):
        """
        Initialize model load error.
        
        Parameters:
            message (str): Error message
            details (Optional[Dict]): Additional error details
        """
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE, details)


class GenerationError(ServiceError):
    """Exception raised when text generation fails."""

    def __init__(self, message: str = "Text generation failed", details: Optional[Dict] = None):
        """
        Initialize generation error.
        
        Parameters:
            message (str): Error message
            details (Optional[Dict]): Additional error details
        """
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR, details)


class ValidationError(ServiceError):
    """Exception raised for validation errors."""

    def __init__(self, message: str = "Validation failed", details: Optional[Dict] = None):
        """
        Initialize validation error.
        
        Parameters:
            message (str): Error message
            details (Optional[Dict]): Additional error details
        """
        super().__init__(message, status.HTTP_400_BAD_REQUEST, details)


async def service_error_handler(request: Request, exc: ServiceError) -> JSONResponse:
    """
    Handle service errors and return JSON response.
    
    Parameters:
        request (Request): FastAPI request object
        exc (ServiceError): Service error exception
        
    Returns:
        JSONResponse: Error response
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "path": str(request.url),
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions and return JSON response.
    
    Parameters:
        request (Request): FastAPI request object
        exc (HTTPException): HTTP exception
        
    Returns:
        JSONResponse: Error response
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP error",
            "detail": exc.detail,
            "path": str(request.url),
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle general exceptions and return JSON response.
    
    Parameters:
        request (Request): FastAPI request object
        exc (Exception): Generic exception
        
    Returns:
        JSONResponse: Error response
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "path": str(request.url),
        },
    )
