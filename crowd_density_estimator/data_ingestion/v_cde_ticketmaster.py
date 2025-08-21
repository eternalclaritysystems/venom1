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


def search_events(keyword=None, latlong=None, radius=25, unit="miles", size=10):
    """
    Search for events using Ticketmaster Discovery API.

    Args:
        keyword (str): Search term (e.g., "concert", "sports").
        latlong (str): Latitude,Longitude string (e.g., "34.0522,-118.2437").
        radius (int): Radius from location.
        unit (str): 'miles' or 'km'.
        size (int): Number of results to return (max 200).

    Returns:
        dict: JSON response from Ticketmaster API.
    """
    params = {
        "apikey": TICKETMASTER_API_KEY,
        "size": size,
        "radius": radius,
        "unit": unit,
    }

    if keyword:
        params["keyword"] = keyword
    if latlong:
        params["latlong"] = latlong

    response = requests.get(BASE_URL, params=params, timeout=10)

    if response.status_code == 200:
        return response.json()
    else:
        raise RuntimeError(
            f"Ticketmaster API error {response.status_code}: {response.text}"
        )


if __name__ == "__main__":
    # Example: search for concerts near Los Angeles
    try:
        data = search_events(keyword="concert", latlong="34.0522,-118.2437", radius=30, size=5)
        events = data.get("_embedded", {}).get("events", [])
        for e in events:
            print(f"{e['name']} | {e['dates']['start']['localDate']} @ {e['_embedded']['venues'][0]['name']}")
    except Exception as ex:
        print(f"Error: {ex}")

# --- Alternative (if you wanted the key directly in Python, not config.yaml) ---
# TICKETMASTER_API_KEY = ""  # << put your API key here if not using config.yaml
