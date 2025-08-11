"""
cleaning_module.py
Cleans raw crowd data for downstream analysis.
"""

import json
from datetime import datetime

def clean_data(raw_rows):
    """
    raw_rows: list of tuples from DB
        (place_id, name, lat, lng, popular_times, live_populartimes)
    Returns: list of dicts
    """
    cleaned = []

    for row in raw_rows:
        place_id, name, lat, lng, ptimes, live = row

        # Skip if coordinates are missing
        if not lat or not lng:
            continue

        # Ensure name is stripped & valid
        if not name:
            continue
        name = name.strip()

        # Parse JSON fields if stored as strings
        if isinstance(ptimes, str):
            try:
                ptimes = json.loads(ptimes)
            except Exception:
                ptimes = None

        if isinstance(live, str):
            try:
                live = json.loads(live)
            except Exception:
                live = None

        # Remove obviously broken data
        if ptimes is not None and not isinstance(ptimes, list):
            ptimes = None
        if live is not None and not isinstance(live, dict):
            live = None

        cleaned.append({
            "place_id": place_id,
            "place_name": name,
            "lat": float(lat),
            "lng": float(lng),
            "popular_times": ptimes,
            "live_data": live,
            "retrieved_at": datetime.utcnow()
        })

    return cleaned
