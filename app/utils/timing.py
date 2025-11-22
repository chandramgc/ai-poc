"""Timing utilities for performance monitoring."""

import asyncio
import functools
import time
from contextlib import contextmanager
from typing import Generator

from app.core.logging import get_logger

logger = get_logger(__name__)


@contextmanager
def timer(operation_name: str) -> Generator:
    """
    Context manager for timing operations.
    
    Parameters:
        operation_name (str): Name of the operation being timed
        
    Yields:
        None
    """
    start_time = time.time()
    try:
        yield
    finally:
        elapsed_time = time.time() - start_time
        logger.info(
            f"{operation_name} completed in {elapsed_time:.3f}s",
            extra={"operation": operation_name, "duration_seconds": elapsed_time}
        )


def measure_latency(func):
    """
    Decorator to measure function execution latency.
    
    Parameters:
        func: Function to measure
        
    Returns:
        Wrapped function with latency measurement
    """
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        latency = (time.time() - start_time) * 1000  # Convert to milliseconds
        logger.debug(
            f"{func.__name__} latency: {latency:.2f}ms",
            extra={"function": func.__name__, "latency_ms": latency}
        )
        return result

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        latency = (time.time() - start_time) * 1000  # Convert to milliseconds
        logger.debug(
            f"{func.__name__} latency: {latency:.2f}ms",
            extra={"function": func.__name__, "latency_ms": latency}
        )
        return result

    # Return appropriate wrapper based on function type
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper
