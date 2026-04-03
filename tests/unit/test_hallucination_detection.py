"""Tests for hallucination detection guardrail."""
from maritime_sentinel.guardrails.hallucination_detection import detect_hallucination


def test_no_hallucination():
    assert detect_hallucination(agent_risk_score=75.0, gold_risk_score=72.0) is False


def test_hallucination_detected():
    assert detect_hallucination(agent_risk_score=95.0, gold_risk_score=50.0) is True


def test_threshold_boundary():
    assert detect_hallucination(agent_risk_score=70.0, gold_risk_score=50.0, threshold=20.0) is False
    assert detect_hallucination(agent_risk_score=71.0, gold_risk_score=50.0, threshold=20.0) is True
