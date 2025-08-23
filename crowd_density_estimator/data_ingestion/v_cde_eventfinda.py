import requests
import yaml
import os
from requests.auth import HTTPBasicAuth

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

EVENTFINDA_API_KEY = config["eventfinda"]["api_key"].strip()
BASE_URL = "https://api.eventfinda.co.nz/v2/events.json"


def search_events(keyword=None, lat=None, lon=None, radius=25, rows=10):
    """
    Search for events using Eventfinda API and normalize the response.
    """
    params = {
        "rows": rows,
        "q": keyword or "",
    }
    # Eventfinda doesn't use lat/lon directly, but you can filter by location text or region IDs
    # You may need to geocode separately and search by region
    # This sample just uses keywords

    response = requests.get(
        BASE_URL,
        params=params,
        auth=HTTPBasicAuth(EVENTFINDA_API_KEY, ""),  # Basic Auth with no password
        timeout=10
    )

    if response.status_code != 200:
        raise RuntimeError(f"Eventfinda API error {response.status_code}: {response.text}")

    data = response.json()
    normalized_events = []

    events = data.get("events", [])
    for e in events:
        title = e.get("name", "No title")
        start = e.get("datetime_start", "No date")
        venue = e.get("venue", {}).get("name", "Unknown venue")
        try:
            location = [float(e.get("point", {}).get("lat", 0)), float(e.get("point", {}).get("lng", 0))]
        except ValueError:
            location = []

        normalized_events.append({
            "title": title,
            "start": start,
            "location": location,
            "venue": venue,
            "source": "Eventfinda",
            "raw": e
        })

    return normalized_events


if __name__ == "__main__":
    try:
        events = search_events(keyword="music", rows=5)
        for e in events:
            print(f"{e['title']} | {e['start']} @ {e['venue']} ({e['location']})")
    except Exception as ex:
        print(f"Error: {ex}")
