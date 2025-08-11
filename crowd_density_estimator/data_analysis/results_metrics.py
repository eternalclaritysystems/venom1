"""
metrics_module.py
Computes a crowd_index and formats data for API storage.
"""

def compute_metrics(tracked_data):
    """
    Adds a crowd_index (0.0 to 1.0) and prepares final result set.
    crowd_index is simply normalized from the live current % (0-100) for now.
    """
    results = []

    for record in tracked_data:
        live = record.get("live_data")
        current_crowd = None
        if live and isinstance(live.get("current"), (int, float)):
            current_crowd = int(live["current"])
            crowd_index = round(current_crowd / 100, 2)
        else:
            current_crowd = None
            crowd_index = None

        results.append({
            "place_id": record["place_id"],
            "place_name": record["place_name"],
            "lat": record["lat"],
            "lng": record["lng"],
            "current_crowd": current_crowd,
            "trend": record.get("trend", "unknown"),
            "crowd_index": crowd_index
        })

    return results
