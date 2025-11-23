"""
FastAPI application entry point.
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description=(
        "A web scraper service that fetches medicine-related news from Google search results. "
        f"Currently using '{settings.scraper_backend}' backend."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1", tags=["search"])


@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    logger.info(f"Starting {settings.app_name}")
    logger.info(f"Scraper backend: {settings.scraper_backend}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Max results: {settings.max_results}")
    logger.info(f"Cache TTL: {settings.cache_ttl}s")
    logger.info(
        "IMPORTANT: This scraper respects rate limits and robots.txt. "
        "Please use responsibly and comply with Google's Terms of Service."
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info(f"Shutting down {settings.app_name}")


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "backend": settings.scraper_backend,
        "docs": "/docs",
        "search_endpoint": "/api/v1/search?q=Insulin&limit=10"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
