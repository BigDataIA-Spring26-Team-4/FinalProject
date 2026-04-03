"""MCP Tool: query_vessel_positions — vessel positions from Redis cache / Snowflake."""


async def query_vessel_positions(mmsi: str | None = None, chokepoint_id: str | None = None) -> list[dict]:
    """Return current/recent positions. Latest positions served from Redis AIS cache."""
    # TODO: Redis vessel:{mmsi} for latest → fallback to Snowflake Silver for history
    raise NotImplementedError
