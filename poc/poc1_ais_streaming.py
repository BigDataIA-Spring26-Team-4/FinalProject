"""
POC 1: AIS Streaming Ingest
============================
Connects to aisstream.io WebSocket, filters by major shipping zones,
and prints live vessel positions.

Prerequisites:
    1. Get free API key from https://aisstream.io (register with email)
    2. Add to .env: AISSTREAM_API_KEY=your_key_here

Usage:
    poetry run python poc/poc1_ais_streaming.py
"""

import asyncio
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

AISSTREAM_URL = "wss://stream.aisstream.io/v0/stream"
API_KEY = os.getenv("AISSTREAM_API_KEY", "")

# Multiple busy shipping zones to ensure data flows
# Format: [[lat_min, lon_min], [lat_max, lon_max]]
BOUNDING_BOXES = {
    "suez_region": [[27.0, 30.0], [32.0, 35.0]],           # Wider Suez + Eastern Med
    "english_channel": [[49.0, -3.0], [51.5, 2.0]],         # Always busy
    "singapore_strait": [[-1.0, 103.0], [2.0, 105.0]],      # Malacca approach
    "hormuz_region": [[24.0, 54.0], [28.0, 58.0]],          # Persian Gulf approach
}

# How long to listen
LISTEN_SECONDS = 45
MAX_MESSAGES = 80


async def stream_ais():
    """Connect to aisstream.io and collect vessel positions."""
    if not API_KEY:
        print("❌ AISSTREAM_API_KEY not set in .env")
        print("   Register for free at https://aisstream.io")
        sys.exit(1)

    try:
        import websockets
    except ImportError:
        print("❌ websockets not installed. Run: poetry install")
        sys.exit(1)

    # Subscribe to all bounding boxes
    all_bboxes = list(BOUNDING_BOXES.values())

    subscribe_msg = {
        "APIKey": API_KEY,
        "BoundingBoxes": all_bboxes,
    }

    vessels = defaultdict(list)
    msg_count = 0

    print(f"🚢 Maritime AI Sentinel — POC 1: AIS Streaming")
    print(f"{'=' * 60}")
    print(f"📡 Connecting to aisstream.io...")
    print(f"🗺️  Monitoring {len(BOUNDING_BOXES)} zones: {', '.join(BOUNDING_BOXES.keys())}")
    print(f"⏱️  Listening for {LISTEN_SECONDS}s (max {MAX_MESSAGES} messages)")
    print(f"{'=' * 60}\n")

    try:
        async with asyncio.timeout(LISTEN_SECONDS + 15):
            async with websockets.connect(AISSTREAM_URL, ping_interval=20, ping_timeout=10) as ws:
                await ws.send(json.dumps(subscribe_msg))
                print("✅ Connected! Waiting for vessel data...\n")

                start = datetime.now(timezone.utc)

                async for raw_msg in ws:
                    elapsed = (datetime.now(timezone.utc) - start).total_seconds()
                    if elapsed > LISTEN_SECONDS or msg_count >= MAX_MESSAGES:
                        break

                    try:
                        msg = json.loads(raw_msg)
                        msg_type = msg.get("MessageType", "")

                        if msg_type != "PositionReport":
                            continue

                        meta = msg.get("MetaData", {})
                        pos = msg.get("Message", {}).get("PositionReport", {})
                        if not pos:
                            continue

                        mmsi = str(meta.get("MMSI", "unknown"))
                        ship_name = meta.get("ShipName", "").strip() or "UNKNOWN"
                        lat = pos.get("Latitude", 0)
                        lon = pos.get("Longitude", 0)
                        speed = pos.get("Sog", 0)
                        heading = pos.get("TrueHeading", 0)

                        record = {
                            "mmsi": mmsi,
                            "ship_name": ship_name,
                            "lat": round(lat, 5),
                            "lon": round(lon, 5),
                            "speed_knots": round(speed, 1),
                            "heading": heading,
                        }

                        vessels[mmsi].append(record)
                        msg_count += 1

                        print(
                            f"  [{msg_count:3d}] {ship_name:<25s} "
                            f"MMSI:{mmsi}  "
                            f"({lat:.4f}, {lon:.4f})  "
                            f"{speed:.1f}kn  "
                            f"{heading}°"
                        )

                    except (json.JSONDecodeError, KeyError):
                        continue

    except asyncio.TimeoutError:
        print(f"\n⏱️  Timeout reached ({LISTEN_SECONDS + 15}s)")
    except Exception as e:
        print(f"\n❌ Connection error: {e}")
        if "403" in str(e) or "401" in str(e):
            print("   Check your AISSTREAM_API_KEY in .env")
        return

    # ── Summary ──
    unique_vessels = len(vessels)
    all_speeds = [r["speed_knots"] for recs in vessels.values() for r in recs if r["speed_knots"] > 0]

    print(f"\n{'=' * 60}")
    print(f"📊 SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Messages received:  {msg_count}")
    print(f"  Unique vessels:     {unique_vessels}")

    if all_speeds:
        print(f"  Avg speed:          {sum(all_speeds) / len(all_speeds):.1f} knots")
        print(f"  Max speed:          {max(all_speeds):.1f} knots")

    if vessels:
        print(f"\n  Top vessels by position count:")
        for mmsi, recs in sorted(vessels.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            print(f"    {recs[0]['ship_name']:<25s} MMSI:{mmsi}  positions:{len(recs)}")

    if msg_count == 0:
        print("\n  ⚠️  No messages received. Possible causes:")
        print("     - API key may be invalid (check https://aisstream.io/dashboard)")
        print("     - Free tier may have limited coverage")
        print("     - Try again in a few minutes")

    print(f"\n✅ POC 1 complete — real-time AIS data from aisstream.io")


if __name__ == "__main__":
    asyncio.run(stream_ais())
