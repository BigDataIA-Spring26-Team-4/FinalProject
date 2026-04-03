"""Alert feed endpoints."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_active_alerts(limit: int = 20):
    """Return active risk alerts across all chokepoints."""
    # TODO: Query Snowflake Gold for recent high-risk events
    raise NotImplementedError
