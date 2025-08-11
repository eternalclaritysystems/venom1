"""
tracking_module.py
Detects trends or anomalies in crowd data.
"""

def detect_trends(cleaned_data):
    """
    Adds a 'trend' field to each record.
    Trend is based on comparing current live data to popular times average.
    """
    tracked = []

    for record in cleaned_data:
        ptimes = record.get("popular_times")
        live = record.get("live_data")

        if not ptimes or not live:
            record["trend"] = "unknown"
            tracked.append(record)
            continue

        # Example: compare current crowd % to average for this hour
        current_crowd = live.get("current")
        hour = live.get("hour")

        try:
            avg_for_hour = 0
            count = 0
            for day_data in ptimes:
                day_hours = day_data.get("data", [])
                if len(day_hours) > hour:
                    avg_for_hour += day_hours[hour]
                    count += 1
            avg_for_hour = avg_for_hour / count if count else 0
        except Exception:
            avg_for_hour = 0

        if current_crowd is None or avg_for_hour == 0:
            record["trend"] = "unknown"
        elif current_crowd > avg_for_hour * 1.1:
            record["trend"] = "increasing"
        elif current_crowd < avg_for_hour * 0.9:
            record["trend"] = "decreasing"
        else:
            record["trend"] = "steady"

        tracked.append(record)

    return tracked
