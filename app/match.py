"""Name matching utilities for the Relationship Finder MCP service."""
import re
import unicodedata
from typing import Optional, Tuple

import pandas as pd
from rapidfuzz import fuzz, process

from app.schemas import ConfidenceLevel


def normalize(name: str) -> str:
    """Normalize a name for comparison.
    
    - Convert to NFKD form and remove diacritics
    - Convert to lowercase
    - Remove punctuation
    - Collapse multiple spaces
    """
    # Decompose Unicode and remove diacritics
    name = unicodedata.normalize("NFKD", name).encode("ASCII", "ignore").decode()
    
    # Convert to lowercase
    name = name.lower()
    
    # Remove punctuation and collapse spaces
    name = re.sub(r"[^\w\s]", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    
    return name


def exact_lookup(df: pd.DataFrame, normalized_name: str) -> Optional[pd.Series]:
    """Look for an exact match (case-insensitive) in the DataFrame."""
    matches = df[df["Name"].str.lower() == normalized_name]
    return matches.iloc[0] if not matches.empty else None


def fuzzy_lookup(df: pd.DataFrame, normalized_name: str) -> Tuple[Optional[pd.Series], float]:
    """Find the best fuzzy match in the DataFrame using rapidfuzz."""
    names = df["Name"].tolist()
    
    # Find the best match using token sort ratio
    best_match, score = process.extractOne(
        normalized_name,
        names,
        scorer=fuzz.WRatio,  # WRatio handles transpositions well
        score_cutoff=50  # Minimum score to consider
    ) or (None, 0.0)
    
    if best_match:
        score = score / 100.0  # Convert score to 0-1 scale
        return df[df["Name"] == best_match].iloc[0], score
    
    return None, 0.0


def confidence_from_score(score: float) -> ConfidenceLevel:
    """Map a matching score to a confidence level."""
    from app.config import get_settings
    
    settings = get_settings()
    
    if score >= settings.HIGH_CONFIDENCE_THRESHOLD:
        return ConfidenceLevel.HIGH
    elif score >= settings.MEDIUM_CONFIDENCE_THRESHOLD:
        return ConfidenceLevel.MEDIUM
    return ConfidenceLevel.LOW