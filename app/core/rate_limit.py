"""
Rate limiting module using token bucket algorithm.
"""

import time
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import HTTPException, Request, status

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class TokenBucket:
    """
    Token bucket rate limiter implementation.
    
    Implements a simple token bucket algorithm for rate limiting.
    """

    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket.
        
        Parameters:
            capacity (int): Maximum number of tokens
            refill_rate (float): Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens from the bucket.
        
        Parameters:
            tokens (int): Number of tokens to consume
            
        Returns:
            bool: True if tokens were consumed, False if insufficient tokens
        """
        now = time.time()
        elapsed = now - self.last_refill

        # Refill tokens based on elapsed time
        self.tokens = min(
            self.capacity, self.tokens + (elapsed * self.refill_rate)
        )
        self.last_refill = now

        # Try to consume tokens
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def get_wait_time(self, tokens: int = 1) -> float:
        """
        Get time to wait until tokens are available.
        
        Parameters:
            tokens (int): Number of tokens needed
            
        Returns:
            float: Wait time in seconds
        """
        if self.tokens >= tokens:
            return 0.0
        
        tokens_needed = tokens - self.tokens
        return tokens_needed / self.refill_rate


class RateLimiter:
    """
    Rate limiter managing multiple token buckets.
    
    Maintains separate token buckets for different keys (IP addresses, API keys).
    """

    def __init__(self, requests_per_minute: int, burst_size: int):
        """
        Initialize rate limiter.
        
        Parameters:
            requests_per_minute (int): Maximum requests per minute
            burst_size (int): Maximum burst size
        """
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.refill_rate = requests_per_minute / 60.0  # tokens per second
        self.buckets: Dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(burst_size, self.refill_rate)
        )

    def check_rate_limit(self, key: str) -> Tuple[bool, float]:
        """
        Check if request is within rate limit.
        
        Parameters:
            key (str): Identifier for rate limiting (IP or API key)
            
        Returns:
            Tuple[bool, float]: (allowed, wait_time_seconds)
        """
        bucket = self.buckets[key]
        
        if bucket.consume():
            return True, 0.0
        
        wait_time = bucket.get_wait_time()
        logger.warning(
            f"Rate limit exceeded for key: {key}. Wait time: {wait_time:.2f}s"
        )
        return False, wait_time

    def clear_bucket(self, key: str):
        """
        Clear token bucket for a specific key.
        
        Parameters:
            key (str): Bucket key to clear
        """
        if key in self.buckets:
            del self.buckets[key]


# Global rate limiter instance
_rate_limiter = None


def get_rate_limiter() -> RateLimiter:
    """
    Get global rate limiter instance.
    
    Returns:
        RateLimiter: Rate limiter instance
    """
    global _rate_limiter
    
    if _rate_limiter is None:
        settings = get_settings()
        _rate_limiter = RateLimiter(
            requests_per_minute=settings.rate_limit.requests_per_minute,
            burst_size=settings.rate_limit.burst_size,
        )
    
    return _rate_limiter


async def rate_limit_dependency(request: Request):
    """
    FastAPI dependency for rate limiting.
    
    Checks rate limit based on client IP or API key.
    
    Parameters:
        request (Request): FastAPI request object
        
    Raises:
        HTTPException: If rate limit is exceeded
    """
    settings = get_settings()
    
    if not settings.rate_limit.enabled:
        return
    
    # Use API key if provided, otherwise use IP address
    api_key = request.headers.get("X-API-Key")
    rate_limit_key = api_key if api_key else request.client.host
    
    limiter = get_rate_limiter()
    allowed, wait_time = limiter.check_rate_limit(rate_limit_key)
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "retry_after": round(wait_time, 2),
            },
        )
