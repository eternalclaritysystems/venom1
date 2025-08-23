import requests
import yaml
import os

# Load configuration from config.yaml
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# Read the API key from config
TICKETMASTER_API_KEY = config["ticketmaster"]["api_key"].strip()

BASE_URL = "https://app.ticketmaster.com/discovery/v2/events.json"


def search_events(keyword=None, lat=None, lon=None, radius=25, unit="miles", size=10):
    """
    Search for events using Ticketmaster Discovery API and normalize the response.

    Args:
        keyword (str): Search term (e.g., "concert", "sports").
        lat (float): Latitude for location-based search.
        lon (float): Longitude for location-based search.
        radius (int): Radius from location.
        unit (str): 'miles' or 'km'.
        size (int): Number of results to return (max 200).

    Returns:
        list[dict]: Normalized list of events.
    """
    params = {
        "apikey": TICKETMASTER_API_KEY,
        "size": size,
        "radius": radius,
        "unit": unit,
    }

    if keyword:
        params["keyword"] = keyword
    if lat is not None and lon is not None:
        params["latlong"] = f"{lat},{lon}"

    response = requests.get(BASE_URL, params=params, timeout=10)

    if response.status_code != 200:
        raise RuntimeError(
            f"Ticketmaster API error {response.status_code}: {response.text}"
        )

    data = response.json()
    normalized_events = []

    events = data.get("_embedded", {}).get("events", [])
    for e in events:
        title = e.get("name", "No title")
        start = e.get("dates", {}).get("start", {}).get("dateTime") or \
                e.get("dates", {}).get("start", {}).get("localDate", "No date")
        
        venue_info = e.get("_embedded", {}).get("venues", [{}])[0]
        venue = venue_info.get("name", "Unknown venue")
        location = []
        if "location" in venue_info:
            lat_str = venue_info["location"].get("latitude")
            lon_str = venue_info["location"].get("longitude")
            if lat_str and lon_str:
                try:
                    location = [float(lat_str), float(lon_str)]
                except ValueError:
                    location = []
        
        normalized_events.append({
            "title": title,
            "start": start,
            "location": location,
            "venue": venue,
            "source": "Ticketmaster",
            "raw": e
        })

    return normalized_events


if __name__ == "__main__":
    try:
        events = search_events(keyword="concert", lat=34.0522, lon=-118.2437, radius=30, size=5)
        for e in events:
            print(f"{e['title']} | {e['start']} @ {e['venue']} ({e['location']})")
    except Exception as ex:
        print(f"Error: {ex}")

# --- Alternative (if you wanted the key directly in Python, not config.yaml) ---
# TICKETMASTER_API_KEY = ""  # << put your API key here if not using config.yaml
