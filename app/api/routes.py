"""
FastAPI routes for the search endpoint.
"""
import hashlib
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.core.cache import cache
from app.core.config import settings
from app.models.article import Article, SearchResponse, ErrorResponse
from app.scraper.google_search import get_scraper, ScraperError, RateLimitError

logger = logging.getLogger(__name__)

router = APIRouter()


def _generate_cache_key(query: str, limit: int) -> str:
    """
    Generate cache key for a search query.
    
    Args:
        query: Search query
        limit: Result limit
        
    Returns:
        Cache key string
    """
    key_string = f"{query}:{limit}:{settings.scraper_backend}"
    return hashlib.md5(key_string.encode()).hexdigest()


@router.get(
    "/search",
    response_model=SearchResponse,
    responses={
        429: {"model": ErrorResponse, "description": "Rate limited by Google"},
        500: {"model": ErrorResponse, "description": "Scraper error"}
    },
    summary="Search for medicine news",
    description=(
        "Search Google News for articles related to a medicine keyword. "
        "Results are cached for improved performance. "
        "Limit defaults to 10 but can be set lower."
    )
)
async def search_articles(
    q: str = Query(
        ...,
        description="Search query (e.g., 'Insulin', 'Metformin')",
        min_length=1,
        max_length=200
    ),
    limit: int = Query(
        10,
        description="Maximum number of results to return",
        ge=1,
        le=settings.max_results
    )
) -> SearchResponse:
    """
    Search for medicine-related news articles.
    
    Args:
        q: Search query keyword (required)
        limit: Maximum number of results (default: 10)
        
    Returns:
        SearchResponse with list of articles
        
    Raises:
        HTTPException: On rate limiting or scraper errors
    """
    logger.info(f"Search request: query='{q}', limit={limit}")
    
    # Check cache first
    cache_key = _generate_cache_key(q, limit)
    cached_results = cache.get(cache_key)
    
    if cached_results is not None:
        logger.info(f"Cache hit for query: {q}")
        return SearchResponse(
            query=q,
            results=cached_results,
            count=len(cached_results),
            cached=True
        )
    
    # Cache miss - fetch from scraper
    try:
        scraper = get_scraper()
        articles = scraper.search(q, limit=limit)
        
        # Cache the results
        cache.set(cache_key, articles)
        
        return SearchResponse(
            query=q,
            results=articles,
            count=len(articles),
            cached=False
        )
        
    except RateLimitError as e:
        logger.error(f"Rate limited: {e}")
        raise HTTPException(
            status_code=429,
            detail={
                "error": "RateLimitError",
                "message": str(e),
                "details": (
                    "Google has detected unusual traffic. "
                    "Please wait before retrying, or consider using "
                    "the Playwright backend for better anti-bot handling."
                )
            }
        )
    except ScraperError as e:
        logger.error(f"Scraper error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "ScraperError",
                "message": str(e),
                "details": "Failed to scrape search results. Please try again later."
            }
        )
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "InternalError",
                "message": "An unexpected error occurred",
                "details": str(e) if settings.debug else None
            }
        )


@router.get(
    "/health",
    summary="Health check",
    description="Check if the service is running"
)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Status message
    """
    return {
        "status": "healthy",
        "backend": settings.scraper_backend,
        "cache_size": cache.size()
    }
