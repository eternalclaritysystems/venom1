import os
import requests
import yaml

# --- Auto-find config.yaml in main/ ---
def find_config_file(start_dir):
    for root, dirs, files in os.walk(start_dir):
        if "config.yaml" in files:
            return os.path.join(root, "config.yaml")
    return None

# Assume project root is one level above data_ingestion/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = find_config_file(PROJECT_ROOT)

if not CONFIG_PATH:
    raise FileNotFoundError(f"Config file not found anywhere in {PROJECT_ROOT}")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# --- API key & defaults ---
TICKETMASTER_API_KEY = config["ticketmaster_token"]
DEFAULT_RADIUS = config.get("default_search_radius", 5000)  # meters

# --- Get current location ---
def get_current_location():
    try:
        response = requests.get("https://ipinfo.io/json")
        if response.status_code == 200:
            lat, lon = map(float, response.json()["loc"].split(","))
            return lat, lon
    except Exception as e:
        print(f"[WARNING] Could not get location automatically: {e}")
    # fallback to NYC
    return 40.7128, -74.0060

# --- Search Ticketmaster events ---
def search_events(keyword=None, radius=DEFAULT_RADIUS):
    lat, lon = get_current_location()
    latlong_str = f"{lat},{lon}"

    # Convert radius from meters to km (Ticketmaster requires 'km' or 'miles')
    radius_km = max(1, int(radius / 1000))  # minimum 1 km

    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    params = {
        "apikey": TICKETMASTER_API_KEY,
        "latlong": latlong_str,
        "radius": radius_km,
        "unit": "km",         # must be 'km' or 'miles'
        "size": 10
    }
    if keyword:
        params["keyword"] = keyword

    response = requests.get(url, params=params, timeout=10)
    if response.status_code == 200:
        return response.json()
    else:
        raise RuntimeError(f"Ticketmaster API error {response.status_code}: {response.text}")

# --- Main execution for testing ---
if __name__ == "__main__":
    try:
        data = search_events(keyword="concert")
        events = data.get("_embedded", {}).get("events", [])
        if not events:
            print("No events found near your location.")
        for e in events:
            venue = e["_embedded"]["venues"][0]["name"]
            date = e["dates"]["start"]["localDate"]
            print(f"{e['name']} | {date} @ {venue}")
    except Exception as ex:
        print(f"[ERROR] {ex}")
