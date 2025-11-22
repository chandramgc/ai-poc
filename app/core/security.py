"""
Security utilities including API key validation and content filtering.
"""

import re
from typing import List, Optional

from fastapi import HTTPException, Header, status

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


# Basic PII patterns (simplified for demo)
PII_PATTERNS = [
    r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
    r"\b\d{16}\b",  # Credit card
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
]

# Basic profanity list (stub - expand as needed)
PROFANITY_LIST = ["badword1", "badword2"]


def validate_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """
    Validate API key from request header.
    
    Parameters:
        x_api_key (Optional[str]): API key from X-API-Key header
        
    Returns:
        str: Validated API key
        
    Raises:
        HTTPException: If API key is missing or invalid
    """
    settings = get_settings()
    
    if not x_api_key:
        logger.warning("Missing API key in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Missing API key", "message": "Provide X-API-Key header"},
        )
    
    if x_api_key != settings.security.api_key:
        logger.warning(f"Invalid API key attempted: {x_api_key[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Invalid API key", "message": "The provided API key is invalid"},
        )
    
    return x_api_key


def validate_prompt_length(prompt: str, max_chars: Optional[int] = None) -> str:
    """
    Validate prompt length.
    
    Parameters:
        prompt (str): Input prompt to validate
        max_chars (Optional[int]): Maximum allowed characters
        
    Returns:
        str: Validated prompt
        
    Raises:
        HTTPException: If prompt exceeds maximum length
    """
    settings = get_settings()
    max_length = max_chars or settings.security.max_prompt_chars
    
    if len(prompt) > max_length:
        logger.warning(f"Prompt exceeds maximum length: {len(prompt)} > {max_length}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Prompt too long",
                "message": f"Prompt must be at most {max_length} characters",
                "current_length": len(prompt),
            },
        )
    
    return prompt


def check_pii(text: str) -> List[str]:
    """
    Check text for potential PII patterns.
    
    Parameters:
        text (str): Text to check for PII
        
    Returns:
        List[str]: List of detected PII pattern types
    """
    detected = []
    
    for pattern in PII_PATTERNS:
        if re.search(pattern, text):
            detected.append(pattern)
    
    return detected


def check_profanity(text: str) -> List[str]:
    """
    Check text for profanity.
    
    Parameters:
        text (str): Text to check for profanity
        
    Returns:
        List[str]: List of detected profane words
    """
    text_lower = text.lower()
    detected = []
    
    for word in PROFANITY_LIST:
        if word in text_lower:
            detected.append(word)
    
    return detected


def filter_content(text: str) -> str:
    """
    Filter content for PII and profanity.
    
    Parameters:
        text (str): Text to filter
        
    Returns:
        str: Original text if validation passes
        
    Raises:
        HTTPException: If PII or profanity is detected and filtering is enabled
    """
    settings = get_settings()
    
    if not settings.security.enable_pii_filter:
        return text
    
    # Check for PII
    pii_detected = check_pii(text)
    if pii_detected:
        logger.warning(f"PII detected in input: {pii_detected}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "PII detected",
                "message": "Input contains potentially sensitive information",
            },
        )
    
    # Check for profanity
    profanity_detected = check_profanity(text)
    if profanity_detected:
        logger.warning(f"Profanity detected in input: {profanity_detected}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Inappropriate content",
                "message": "Input contains inappropriate language",
            },
        )
    
    return text


def sanitize_output(text: str) -> str:
    """
    Sanitize model output (placeholder for future logic).
    
    Parameters:
        text (str): Text to sanitize
        
    Returns:
        str: Sanitized text
    """
    # TODO: Implement output sanitization if needed
    # For now, just return the original text
    return text
