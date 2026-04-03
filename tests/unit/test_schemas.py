"""Tests for Pydantic output schemas."""
from datetime import datetime
from maritime_sentinel.agents.schemas import RiskScore, Citation, SanctionsMatch


def test_risk_score_valid():
    score = RiskScore(
        region="middle_east",
        composite_score=75.0,
        geopolitical_score=80.0,
        weather_score=20.0,
        sanctions_score=50.0,
        conflict_score=85.0,
        timestamp=datetime.now(),
        citations=[],
        requires_hitl=True,
    )
    assert score.composite_score == 75.0
    assert score.requires_hitl is True


def test_risk_score_bounds():
    """Score must be 0-100."""
    import pytest
    with pytest.raises(Exception):
        RiskScore(
            region="test",
            composite_score=150.0,  # Out of bounds
            geopolitical_score=0, weather_score=0, sanctions_score=0, conflict_score=0,
            timestamp=datetime.now(), citations=[],
        )


def test_citation_confidence_bounds():
    citation = Citation(source_id="gdelt_123", source_type="gdelt", text_snippet="test", confidence=0.95)
    assert citation.confidence == 0.95
