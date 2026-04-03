"""Redis client — caching layer for Gold queries, MCP tool responses, and AIS positions."""

import json

import redis

from maritime_sentinel.config import settings


def get_redis_client() -> redis.Redis:
    """Return a Redis client connected to the Docker service."""
    return redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        decode_responses=True,
    )


def cache_get(key: str) -> dict | None:
    """Get a cached value by key. Returns None on miss."""
    r = get_redis_client()
    val = r.get(key)
    return json.loads(val) if val else None


def cache_set(key: str, value: dict, ttl: int | None = None) -> None:
    """Set a cached value with TTL. Defaults to Gold cache TTL from settings."""
    r = get_redis_client()
    r.setex(key, ttl or settings.redis_gold_cache_ttl, json.dumps(value))


def update_vessel_position(mmsi: str, position: dict) -> None:
    """Update the latest position for a vessel in Redis."""
    r = get_redis_client()
    r.setex(f"vessel:{mmsi}", settings.redis_ais_position_ttl, json.dumps(position))


def get_vessel_position(mmsi: str) -> dict | None:
    """Get the latest cached position for a vessel."""
    return cache_get(f"vessel:{mmsi}")
