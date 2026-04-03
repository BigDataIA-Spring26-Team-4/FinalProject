"""Redis client — caching layer for Gold queries, MCP tool responses, and AIS positions."""
import json
import redis
from maritime_sentinel.config import settings

GOLD_CACHE_TTL = 300       # 5 minutes
MCP_TOOL_CACHE_TTL = 120   # 2 minutes
AIS_POSITION_TTL = 120     # 2 minutes


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


def cache_set(key: str, value: dict, ttl: int = GOLD_CACHE_TTL) -> None:
    """Set a cached value with TTL."""
    r = get_redis_client()
    r.setex(key, ttl, json.dumps(value))


def update_vessel_position(mmsi: str, position: dict) -> None:
    """Update the latest position for a vessel in Redis."""
    r = get_redis_client()
    r.setex(f"vessel:{mmsi}", AIS_POSITION_TTL, json.dumps(position))


def get_vessel_position(mmsi: str) -> dict | None:
    """Get the latest cached position for a vessel."""
    return cache_get(f"vessel:{mmsi}")
