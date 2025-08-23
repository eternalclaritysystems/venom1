import requests
import yaml
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

SONGKICK_API_KEY = config["songkick"]["api_key"].strip()
BASE_URL = "https://api.songkick.com/api/3.0/events.json"


def search_events(keyword=None, lat=None, lon=None, radius=25, per_page=10):
    """
    Search for events using Songkick API and normalize the response.
    NOTE: Songkick primarily searches by location (metro_area_id) or geo coords.
    """
    params = {
        "apikey": SONGKICK_API_KEY,
        "per_page": per_page
    }
    if keyword:
        params["query"] = keyword
    if lat is not None and lon is not None:
        params["location"] = f"geo:{lat},{lon}"
    else:
        params["location"] = "clientip"  # fallback: based on requester IP

    response = requests.get(BASE_URL, params=params, timeout=10)
    if response.status_code != 200:
        raise RuntimeError(f"Songkick API error {response.status_code}: {response.text}")

    data = response.json()
    normalized_events = []

    events = data.get("resultsPage", {}).get("results", {}).get("event", [])
    for e in events:
        title = e.get("displayName", "No title")
        start = e.get("start", {}).get("datetime") or e.get("start", {}).get("date", "No date")
        venue = e.get("venue", {}).get("displayName", "Unknown venue")
        try:
            location = [float(e.get("location", {}).get("lat", 0)), float(e.get("location", {}).get("lng", 0))]
        except ValueError:
            location = []

        normalized_events.append({
            "title": title,
            "start": start,
            "location": location,
            "venue": venue,
            "source": "Songkick",
            "raw": e
        })

    return normalized_events


if __name__ == "__main__":
    try:
        events = search_events(keyword="rock", lat=34.0522, lon=-118.2437, radius=30, per_page=5)
        for e in events:
            print(f"{e['title']} | {e['start']} @ {e['venue']} ({e['location']})")
    except Exception as ex:
        print(f"Error: {ex}")
