"""MCP Tool: get_weather_alerts — active severe weather for a chokepoint."""


async def get_weather_alerts(chokepoint_id: str) -> list[dict]:
    """Return active weather alerts for a chokepoint region."""
    # TODO: Query Snowflake silver_weather_alerts filtered by chokepoint + not expired
    raise NotImplementedError
