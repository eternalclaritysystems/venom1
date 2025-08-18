import os
import sys

DATA_FOLDER = os.path.join(os.path.dirname(__file__))  # the data_ingestion folder
CONFIG_PATH = os.path.join(DATA_FOLDER, "config.yaml")

if not os.path.isfile(CONFIG_PATH):
    print("Error: config.yaml file not found in data_ingestion folder.")
    sys.exit(1)

# From here, load config.yaml and continue with Eventbrite API logic
import yaml
import requests

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

EVENTBRITE_TOKEN = config.get("eventbrite_token")
if not EVENTBRITE_TOKEN:
    print("Error: eventbrite_token not set in config.yaml")
    sys.exit(1)

# Example function to fetch events
def fetch_eventbrite(lat, lng, radius_meters):
    headers = {"Authorization": f"Bearer {EVENTBRITE_TOKEN}"}
    radius_miles = radius_meters / 1609.34
    params = {
        "location.latitude": lat,
        "location.longitude": lng,
        "location.within": f"{radius_miles}mi",
        "expand": "venue",
        "sort_by": "date"
    }
    url = "https://www.eventbriteapi.com/v3/events/search/"
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json().get("events", [])

if __name__ == "__main__":
    print("This module can be imported by data_ingestion_main.py for Eventbrite ingestion.")
