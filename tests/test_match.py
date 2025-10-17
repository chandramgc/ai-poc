"""Test matching utilities."""
import pytest

from app.match import confidence_from_score, normalize
from app.schemas import ConfidenceLevel


@pytest.mark.parametrize("name,expected", [
    ("Saanvi", "saanvi"),
    ("Saanvee", "saanvee"),
    ("M. Srinivas", "m srinivas"),
    ("Mallula   Srinivas", "mallula srinivas"),
    ("Üsha Rani", "usha rani"),
    ("Srīnivas", "srinivas"),
])
def test_normalize(name: str, expected: str):
    """Test name normalization."""
    assert normalize(name) == expected


@pytest.mark.parametrize("score,expected_confidence", [
    (1.0, ConfidenceLevel.HIGH),
    (0.96, ConfidenceLevel.HIGH),
    (0.85, ConfidenceLevel.MEDIUM),
    (0.75, ConfidenceLevel.LOW),
])
def test_confidence_from_score(score: float, expected_confidence: ConfidenceLevel):
    """Test confidence level mapping."""
    assert confidence_from_score(score) == expected_confidence