"""Name matching utilities for the Relationship Finder MCP service."""
import logging
import re
import unicodedata
from typing import Optional, Tuple

import pandas as pd
from rapidfuzz import fuzz, process

from app.schemas import ConfidenceLevel

logger = logging.getLogger(__name__)


def normalize(name: str) -> str:
    """Normalize a name for comparison.
    
    - Convert to NFKD form and remove diacritics
    - Convert to lowercase
    - Remove punctuation
    - Collapse multiple spaces
    """
    if not name:
        logger.warning("Received empty name for normalization")
        return ""
        
    logger.debug(f"Normalizing name: '{name}'")
    
    # Decompose Unicode and remove diacritics
    normalized = unicodedata.normalize("NFKD", name).encode("ASCII", "ignore").decode()
    logger.debug(f"After Unicode normalization: '{normalized}'")
    
    # Convert to lowercase
    normalized = normalized.lower()
    logger.debug(f"After lowercase: '{normalized}'")
    
    # Remove punctuation and collapse spaces
    normalized = re.sub(r"[^\w\s]", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    logger.debug(f"After cleaning: '{normalized}'")
    
    return normalized


def exact_lookup(df: pd.DataFrame, normalized_name: str) -> Optional[pd.Series]:
    """Look for an exact match (case-insensitive) in the DataFrame."""
    logger.debug(f"\nLooking for exact match for '{normalized_name}'")
    logger.debug(f"DataFrame columns: {df.columns.tolist()}")
    logger.debug(f"DataFrame shape: {df.shape}")
    logger.debug(f"First few names:\n{df['Name'].head().tolist()}")
    
    # Convert input names to normalized form for comparison
    df_names = df["Name"].apply(normalize)
    logger.debug(f"\nNormalized names in DataFrame:")
    for orig, norm in zip(df["Name"].head(), df_names.head()):
        logger.debug(f"  {orig!r} -> {norm!r}")
    
    matches = df[df_names == normalized_name]
    logger.debug(f"\nFound {matches.shape[0]} exact matches")
    
    if not matches.empty:
        result = matches.iloc[0]
        logger.debug(f"Returning match: {dict(result)}")
        return result
    logger.debug("No exact match found")
    return None


def fuzzy_lookup(df: pd.DataFrame, normalized_name: str) -> Optional[Tuple[pd.Series, ConfidenceLevel]]:
    """Look for a fuzzy match in the DataFrame using fuzz ratio."""
    print(f"\nStarting fuzzy lookup for '{normalized_name}'")
    
    if df.empty:
        logger.warning("DataFrame is empty")
        return None

    # Convert input names to normalized form for comparison
    df_names = df["Name"].apply(normalize)
    logger.debug(f"\nTop normalized names in DataFrame:")
    for orig, norm in zip(df["Name"].head(), df_names.head()):
        logger.debug(f"  {orig!r} -> {norm!r}")

    if not df_names.tolist():  # Ensure we have names to match against
        logger.warning("No names found after normalization")
        return None

    # Find best match
    match, score = process.extractOne(
        normalized_name,
        df_names,
        scorer=fuzz.ratio
    )
    logger.debug(f"Best fuzzy match: '{match}' with score {score}")

    if score >= 90:
        confidence = ConfidenceLevel.HIGH
    elif score >= 70:
        confidence = ConfidenceLevel.MEDIUM
    elif score >= 50:
        confidence = ConfidenceLevel.LOW
    else:
        logger.debug(f"Score {score} below threshold, no match returned")
        return None

    match_idx = df_names[df_names == match].index[0]
    result = df.iloc[match_idx]
    logger.debug(f"Returning match {dict(result)} with {confidence.value} confidence")
    return result, confidence


def confidence_from_score(score: float) -> ConfidenceLevel:
    """Map a matching score to a confidence level."""
    if score >= 0.9:
        return ConfidenceLevel.HIGH
    elif score >= 0.7:
        return ConfidenceLevel.MEDIUM
    return ConfidenceLevel.LOW