import requests
import yaml
import os

# Load configuration from config.yaml
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# Read the API key from config
PREDICTHQ_API_KEY = config["predicthq"]["api_key"].strip()

BASE_URL = "https://api.predicthq.com/v1/events"


def search_events(keyword=None, lat=None, lon=None, radius="25mi", limit=10, category=None):
    """
    Search for events using PredictHQ API and normalize the response.

    Args:
        keyword (str): Search term (e.g., "concert", "sports").
        lat (float): Latitude for location-based search.
        lon (float): Longitude for location-based search.
        radius (str): Search radius, with units (e.g., "25mi" or "40km").
        limit (int): Max number of results to return.
        category (str): Optional PredictHQ event category (e.g., "concerts", "sports").

    Returns:
        list[dict]: Normalized list of events.
    """
    headers = {
        "Authorization": f"Bearer {PREDICTHQ_API_KEY}",
        "Accept": "application/json"
    }
    
    params = {
        "limit": limit,
        "sort": "start",
    }

    if keyword:
        params["q"] = keyword
    if lat is not None and lon is not None:
        params["within"] = f"{radius}@{lat},{lon}"
    if category:
        params["category"] = category

    response = requests.get(BASE_URL, headers=headers, params=params, timeout=10)

    if response.status_code != 200:
        raise RuntimeError(
            f"PredictHQ API error {response.status_code}: {response.text}"
        )

    data = response.json()
    normalized_events = []

    for e in data.get("results", []):
        title = e.get("title", "No title")
        start = e.get("start", "No date")
        location = e.get("location", [])
        venue = e.get("entities", [{}])[0].get("name") if e.get("entities") else "Unknown venue"

        normalized_events.append({
            "title": title,
            "start": start,
            "location": location,
            "venue": venue,
            "source": "PredictHQ",
            "raw": e
        })

    return normalized_events


if __name__ == "__main__":
    try:
        events = search_events(keyword="concert", lat=34.0522, lon=-118.2437, radius="30mi", limit=5)
        for e in events:
            print(f"{e['title']} | {e['start']} @ {e['venue']} ({e['location']})")
    except Exception as ex:
        print(f"Error: {ex}")
