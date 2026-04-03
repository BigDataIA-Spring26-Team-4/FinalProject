"""MCP Tool: get_conflict_events — recent ACLED events for a region."""


async def get_conflict_events(region: str, days_back: int = 30) -> list[dict]:
    """Return recent conflict events from ACLED for a region."""
    # TODO: Query Snowflake silver_conflict_events with geo filter
    raise NotImplementedError
