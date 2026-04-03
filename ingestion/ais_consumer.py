"""AIS WebSocket streaming consumer.

Connects to aisstream.io, filters positions by chokepoint bounding boxes,
batches 1000 positions, and writes to Snowflake Bronze + Redis latest position cache.
"""
import asyncio
import json
import os
import structlog

logger = structlog.get_logger()

AISSTREAM_URL = "wss://stream.aisstream.io/v0/stream"
API_KEY = os.getenv("AISSTREAM_API_KEY", "")

# Chokepoint bounding boxes — loaded from dim_chokepoints at startup
# Format: [[lat_min, lon_min], [lat_max, lon_max]]
CHOKEPOINT_BBOXES = {
    "suez": [[29.5, 32.0], [31.5, 33.5]],
    "hormuz": [[25.5, 55.5], [27.0, 57.5]],
    "malacca": [[0.5, 100.0], [4.0, 104.5]],
    "bab_el_mandeb": [[12.0, 43.0], [13.5, 44.0]],
    "panama": [[8.5, -80.0], [9.5, -79.0]],
    # TODO: Load remaining chokepoints from dim_chokepoints at startup
}

BATCH_SIZE = 1000
FLUSH_INTERVAL_SECONDS = 60


async def connect_and_stream():
    """Main streaming loop."""
    import websockets

    subscribe_msg = {
        "APIKey": API_KEY,
        "BoundingBoxes": [bbox for bbox in CHOKEPOINT_BBOXES.values()],
    }

    batch: list[dict] = []

    async with websockets.connect(AISSTREAM_URL) as ws:
        await ws.send(json.dumps(subscribe_msg))
        logger.info("Connected to aisstream.io", chokepoints=list(CHOKEPOINT_BBOXES.keys()))

        async for raw_msg in ws:
            try:
                msg = json.loads(raw_msg)
                position = _parse_position(msg)
                if position:
                    batch.append(position)

                if len(batch) >= BATCH_SIZE:
                    await _flush_batch(batch)
                    batch = []
            except Exception as e:
                logger.error("Error processing AIS message", error=str(e))


def _parse_position(msg: dict) -> dict | None:
    """Extract vessel position from aisstream message."""
    try:
        meta = msg.get("MetaData", {})
        position_report = msg.get("Message", {}).get("PositionReport", {})
        if not position_report:
            return None

        return {
            "mmsi": meta.get("MMSI"),
            "ship_name": meta.get("ShipName", "").strip(),
            "lat": position_report.get("Latitude"),
            "lon": position_report.get("Longitude"),
            "speed": position_report.get("Sog"),
            "heading": position_report.get("TrueHeading"),
            "timestamp": meta.get("time_utc"),
        }
    except Exception:
        return None


async def _flush_batch(batch: list[dict]):
    """Write batch to Snowflake Bronze + update Redis latest position cache."""
    logger.info("Flushing AIS batch", count=len(batch))
    # TODO: Write to Snowflake via staged CSV
    # TODO: Update Redis vessel:{mmsi} keys


if __name__ == "__main__":
    asyncio.run(connect_and_stream())
