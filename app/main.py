"""
Main FastAPI application.

Production-ready LLM service with observability, rate limiting, and security.
"""

import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

from app.api.routers import chat, health, inference
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.llm.loader import load_pipeline, unload_pipeline
from app.utils.errors import (
    ServiceError,
    general_exception_handler,
    http_exception_handler,
    service_error_handler,
)

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Prometheus metrics
requests_total = Counter(
    "http_requests_total", 
    "Total HTTP requests", 
    ["method", "endpoint", "status"]
)
tokens_generated_total = Counter(
    "tokens_generated_total", 
    "Total tokens generated",
    ["model"]
)
request_latency = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    
    Parameters:
        app (FastAPI): FastAPI application instance
        
    Yields:
        None
    """
    # Startup
    logger.info("Starting up LLM FastAPI service")
    settings = get_settings()
    
    try:
        logger.info(f"Loading model: {settings.model.name}")
        load_pipeline()
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model during startup: {str(e)}")
        logger.warning("Service starting without model - health checks will report unhealthy")
    
    yield
    
    # Shutdown
    logger.info("Shutting down LLM FastAPI service")
    unload_pipeline()
    logger.info("Service shut down complete")


# Create FastAPI app
settings = get_settings()
app = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
    description="Production-ready FastAPI service for Hugging Face LLM deployment",
    lifespan=lifespan,
)


# Exception handlers
app.add_exception_handler(ServiceError, service_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# Middleware for timing and metrics
@app.middleware("http")
async def add_timing_and_metrics(request: Request, call_next):
    """
    Middleware for request timing and metrics collection.
    
    Parameters:
        request (Request): Incoming request
        call_next: Next middleware or route handler
        
    Returns:
        Response: HTTP response with timing header
    """
    start_time = time.time()
    
    # Process request
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        status_code = 500
        raise
    finally:
        # Calculate latency
        latency = time.time() - start_time
        
        # Record metrics
        requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            status=status_code
        ).inc()
        
        request_latency.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(latency)
        
        # Log request
        logger.info(
            f"{request.method} {request.url.path} - {status_code}",
            extra={
                "method": request.method,
                "route": request.url.path,
                "status_code": status_code,
                "latency_ms": round(latency * 1000, 2),
            }
        )
    
    # Add timing header
    response.headers["X-Process-Time"] = f"{latency:.3f}"
    return response


# Include routers
app.include_router(health.router)
app.include_router(inference.router)
app.include_router(chat.router)


# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.
    
    Returns:
        Response: Prometheus-formatted metrics
    """
    if not settings.metrics.enabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Metrics endpoint is disabled"
        )
    
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with service information.
    
    Returns:
        dict: Service information
    """
    return {
        "service": settings.app.name,
        "version": settings.app.version,
        "model": settings.model.name,
        "status": "running",
        "docs": "/docs",
    }


def main():
    """Run the application with uvicorn."""
    settings = get_settings()
    
    logger.info(f"Starting {settings.app.name} v{settings.app.version}")
    logger.info(f"Host: {settings.app.host}:{settings.app.port}")
    logger.info(f"Model: {settings.model.name}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        log_level=settings.app.log_level.lower(),
        reload=False,
    )


if __name__ == "__main__":
    main()
