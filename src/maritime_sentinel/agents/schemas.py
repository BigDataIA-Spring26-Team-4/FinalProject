"""Pydantic output schemas for all agents — enforced by guardrails."""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class Citation(BaseModel):
    """A source citation backing a factual claim."""
    source_id: str
    source_type: Literal["gdelt", "acled", "ofac", "weather", "ais"]
    text_snippet: str
    confidence: float = Field(ge=0, le=1)


class RiskScore(BaseModel):
    """Composite risk assessment for a region or chokepoint."""
    region: str
    composite_score: float = Field(ge=0, le=100)
    geopolitical_score: float = Field(ge=0, le=100)
    weather_score: float = Field(ge=0, le=100)
    sanctions_score: float = Field(ge=0, le=100)
    conflict_score: float = Field(ge=0, le=100)
    timestamp: datetime
    citations: list[Citation]
    requires_hitl: bool = False


class RouteAdvisory(BaseModel):
    """Rerouting recommendation for a specific vessel."""
    vessel_mmsi: str
    current_route: str
    recommended_route: str
    additional_days: float
    additional_cost_usd: float
    risk_reduction: float
    reasoning: str
    citations: list[Citation]
    requires_hitl: bool = True  # Always requires human approval


class SanctionsMatch(BaseModel):
    """Result of sanctions screening for a vessel or entity."""
    entity_name: str
    entity_type: Literal["vessel", "company", "individual"]
    match_confidence: float = Field(ge=0, le=1)
    matched_programs: list[str]
    citations: list[Citation]
    requires_hitl: bool = False  # True if confidence 0.85-0.95


class WeatherAlert(BaseModel):
    """Weather impact assessment for a shipping route."""
    chokepoint_id: str
    severity: Literal["low", "moderate", "high", "extreme"]
    event_type: str
    impact_summary: str
    valid_until: datetime
    citations: list[Citation]
