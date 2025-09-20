# src/clean.py
import pandas as pd


def clean_data(events: list) -> pd.DataFrame:
    """
    Normalize raw Ticketmaster event data into a flat DataFrame
    with consistent lat/lon, name, date, venue fields.
    """
    rows = []
    for ev in events:
        try:
            name = ev.get("name")
            dates = ev.get("dates", {}).get("start", {}).get("localDate")
            venue = ev.get("_embedded", {}).get("venues", [{}])[0]

            lat = venue.get("location", {}).get("latitude")
            lon = venue.get("location", {}).get("longitude")

            # Skip if no coords
            if not lat or not lon:
                continue

            rows.append({
                "name": name,
                "date": dates,
                "venue": venue.get("name"),
                "lat": float(lat),   # ✅ standardized
                "lon": float(lon),   # ✅ standardized
            })
        except Exception:
            continue

    df = pd.DataFrame(rows)
    print(f"[clean] Cleaned dataset contains {len(df)} rows.")
    return df
