"""Vessel tracking endpoints."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/{mmsi}")
async def get_vessel(mmsi: str):
    """Return current position and risk profile for a vessel."""
    # TODO: Query Redis AIS cache + Snowflake vessel risk profile
    raise NotImplementedError
