"""Hallucination detection — cross-check agent scores against Snowflake Gold."""


def detect_hallucination(agent_risk_score: float, gold_risk_score: float, threshold: float = 20.0) -> bool:
    """Return True if agent score deviates from Gold aggregate by more than threshold."""
    return abs(agent_risk_score - gold_risk_score) > threshold
