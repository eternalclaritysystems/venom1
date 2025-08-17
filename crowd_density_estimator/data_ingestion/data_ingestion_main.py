#!/usr/bin/env python3
"""
data_ingestion_main.py

Simple Eventbrite event ingestion within a given lat/lng + radius.
Logs results to console (or database if you add that later).
"""

import sys
import requests
import yaml
import logging

# Load config
try:
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    sys.stderr.write("Error: config.yaml file not found.\n")
    sys.exit(1)

EVENTBRITE_TOKEN = config.get("eventbrite_token")
DEFAULT_RADIUS = config.get("default_search_radius", 5000)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("data_ingestion_main")

def fetch_eventbrite_events(lat, lng, radius_meters):
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
    events = resp.json().get("events", [])
    coords = []
    for ev in events:
        venue = ev.get("venue", {})
        vlat = venue.get("latitude")
        vlng = venue.get("longitude")
        name = ev.get("name", {}).get("text", "Unnamed")
        if vlat and vlng:
            coords.append((name, float(vlat), float(vlng)))
    return coords

def ingest(lat, lng, radius):
    events = fetch_eventbrite_events(lat, lng, radius)
    if not events:
        logger.warning("No Eventbrite events found.")
        return
    logger.info(f"Found {len(events)} events near {lat},{lng}")
    for name, vlat, vlng in events:
        logger.info(f"- {name} at {vlat},{vlng}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 data_ingestion_main.py LATITUDE LONGITUDE [RADIUS_METERS]")
        print(f"Default radius (meters): {DEFAULT_RADIUS}")
        sys.exit(1)

    lat = float(sys.argv[1])
    lng = float(sys.argv[2])
    radius = int(sys.argv[3]) if len(sys.argv) >= 4 else DEFAULT_RADIUS

    ingest(lat, lng, radius)
