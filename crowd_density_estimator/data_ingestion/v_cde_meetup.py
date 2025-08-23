import requests
import yaml
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

MEETUP_API_KEY = config["meetup"]["api_key"].strip()
BASE_URL = "https://api.meetup.com/find/upcoming_events"


def search_events(keyword=None, lat=None, lon=None, radius=25, page=10):
    """
    Search for events using Meetup API and normalize the response.
    """
    params = {
        "key": MEETUP_API_KEY,
        "page": page,
        "radius": radius,
    }
    if keyword:
        params["text"] = keyword
    if lat is not None and lon is not None:
        params["lat"] = lat
        params["lon"] = lon

    response = requests.get(BASE_URL, params=params, timeout=10)
    if response.status_code != 200:
        raise RuntimeError(f"Meetup API error {response.status_code}: {response.text}")

    data = response.json()
    normalized_events = []

    events = data.get("events", [])
    for e in events:
        title = e.get("name", "No title")
        start = e.get("local_date", "No date") + "T" + e.get("local_time", "00:00") \
                if e.get("local_date") else e.get("time", "No date")
        venue = e.get("venue", {}).get("name", "Unknown venue")
        try:
            location = [float(e.get("venue", {}).get("lat", 0)), float(e.get("venue", {}).get("lon", 0))]
        except ValueError:
            location = []

        normalized_events.append({
            "title": title,
            "start": start,
            "location": location,
            "venue": venue,
            "source": "Meetup",
            "raw": e
        })

    return normalized_events


if __name__ == "__main__":
    try:
        events = search_events(keyword="tech", lat=37.7749, lon=-122.4194, radius=30, page=5)
        for e in events:
            print(f"{e['title']} | {e['start']} @ {e['venue']} ({e['location']})")
    except Exception as ex:
        print(f"Error: {ex}")
