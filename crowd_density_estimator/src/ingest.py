# src/ingest.py
import requests


def from_ticketmaster(api_key: str, radius: int = 30, days: int = 30) -> list:
    """
    Fetch events from Ticketmaster Discovery API.
    Returns a list of event dictionaries.
    """
    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    params = {
        "apikey": api_key,
        "radius": radius,
        "unit": "miles",
        "locale": "*",
        "size": 200,  # max per page
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            print(f"[ingest] Ticketmaster API error: {resp.status_code}")
            return []

        data = resp.json()

        events = data.get("_embedded", {}).get("events", [])
        print(f"[ingest] Loaded {len(events)} events from Ticketmaster API")
        return events  #  return list of dicts

    except Exception as e:
        print(f"[ingest] Error fetching data: {e}")
        return []
