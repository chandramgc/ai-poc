"""
Health check router.

Provides endpoints for service health and status monitoring.
"""

from fastapi import APIRouter

from app.api.schemas import HealthResponse, StatusResponse
from app.core.cache import get_cache
from app.core.config import get_settings
from app.core.logging import get_logger
from app.llm.loader import _pipeline

logger = get_logger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns service health status and model availability.
    
    Returns:
        HealthResponse: Health status information
    """
    settings = get_settings()
    model_loaded = _pipeline is not None
    
    return HealthResponse(
        status="healthy" if model_loaded else "unhealthy",
        model_loaded=model_loaded,
        model_name=settings.model.name,
    )


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """
    Get detailed service status.
    
    Returns comprehensive service status including cache statistics.
    
    Returns:
        StatusResponse: Detailed status information
    """
    settings = get_settings()
    cache = get_cache()
    
    return StatusResponse(
        service_name=settings.app.name,
        version=settings.app.version,
        model_name=settings.model.name,
        model_device=settings.model.device,
        cache_stats=cache.get_stats(),
        rate_limit_enabled=settings.rate_limit.enabled,
    )
