"""Risk score endpoints."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/chokepoint/{chokepoint_id}")
async def get_chokepoint_risk(chokepoint_id: str, timeframe_days: int = 7):
    """Return composite risk score for a maritime chokepoint."""
    # TODO: Query Snowflake Gold via Redis cache
    raise NotImplementedError
