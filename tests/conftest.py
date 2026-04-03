"""Shared pytest fixtures for Maritime AI Sentinel tests."""
import pytest


@pytest.fixture
def sample_ais_position():
    """Sample AIS position data for testing."""
    return {
        "mmsi": "123456789",
        "ship_name": "TEST VESSEL",
        "lat": 30.0,
        "lon": 32.5,
        "speed": 12.5,
        "heading": 180,
        "timestamp": "2026-04-03T12:00:00Z",
    }


@pytest.fixture
def sample_chokepoint():
    """Sample chokepoint data for testing."""
    return {
        "chokepoint_id": "suez",
        "name": "Suez Canal",
        "region": "middle_east",
        "bbox": {"lat_min": 29.5, "lon_min": 32.0, "lat_max": 31.5, "lon_max": 33.5},
        "pct_global_trade": 12.0,
    }


@pytest.fixture
def sample_risk_score():
    """Sample risk score for testing guardrails."""
    return {
        "region": "middle_east",
        "composite_score": 72.5,
        "geopolitical_score": 85.0,
        "weather_score": 30.0,
        "sanctions_score": 60.0,
        "conflict_score": 80.0,
    }
