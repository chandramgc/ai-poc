"""
Dependency injection utilities for FastAPI.
"""

from typing import Annotated

from fastapi import Depends

from app.core.rate_limit import rate_limit_dependency
from app.core.security import validate_api_key

# Dependency for API key validation
APIKeyDep = Annotated[str, Depends(validate_api_key)]

# Dependency for rate limiting
RateLimitDep = Annotated[None, Depends(rate_limit_dependency)]
