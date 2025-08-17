#!/usr/bin/env python3
"""
crowd_ingestion.py

Dynamic crowd/popularity data ingestion within a given lat/lng + radius.
Stores data in PostgreSQL with PostGIS extension for spatial queries.

Usage:
  python3 crowd_ingestion.py LATITUDE LONGITUDE [RADIUS_METERS]

If no radius provided, uses default from config.yaml.
"""

import sys
import logging
import requests
import yaml
import psycopg2
from psycopg2.extras import execute_values
from populartimes import get as gp_get
from livepopulartimes import get_live_populartimes

# Load config
try:
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    sys.stderr.write("Error: config.yaml file not found.\n")
    sys.exit(1)

EVENTBRITE_TOKEN = config["eventbrite_token"]
GOOGLE_API_KEY = config["google_api_key"]
DB_CONFIG = config["database"]
DEFAULT_RADIUS = config.get("default_search_radius", 5000)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("crowd_ingestion")

# DB connection helper
def get_db_conn():
    return psycopg2.connect(**DB_CONFIG)

# Initialize DB with PostGIS and table for spatial queries
def init_db():
    with get_db_conn() as conn:
        with conn.cursor() as cur:
            # Enable PostGIS extension (if not enabled)
            cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
            # Create table with geography column for efficient radius queries
            cur.execute("""
                CREATE TABLE IF NOT EXISTS crowd_popularity (
                    id SERIAL PRIMARY KEY,
                    place_id TEXT UNIQUE,
                    name TEXT,
                    lat DOUBLE PRECISION,
                    lng DOUBLE PRECISION,
                    location GEOGRAPHY(POINT, 4326),
                    retrieved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    popular_times JSONB,
                    live_populartimes JSONB
                );
            """)
            # Index on location for fast spatial queries
            cur.execute("CREATE INDEX IF NOT EXISTS idx_crowdpop_location ON crowd_popularity USING GIST(location);")
        conn.commit()

# Fetch Eventbrite events within radius of lat/lng
def fetch_eventbrite_venues(lat, lng, radius_meters):
    headers = {"Authorization": f"Bearer {EVENTBRITE_TOKEN}"}
    # Eventbrite expects radius in miles or km, convert meters to miles (approx)
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
    data = resp.json().get("events", [])
    coords = set()
    for ev in data:
        venue = ev.get("venue", {})
        vlat = venue.get("latitude")
        vlng = venue.get("longitude")
        if vlat and vlng:
            coords.add((float(vlat), float(vlng)))
    logger.info(f"[Eventbrite] Found {len(coords)} venues near {lat},{lng} within {radius_meters}m")
    return coords

# Fetch Google Popular Times places around lat/lng within radius
def fetch_google_populartimes(lat, lng, radius_meters):
    # populartimes lib expects radius as integer meters
    places = gp_get(GOOGLE_API_KEY, lat=lat, lng=lng, radius=radius_meters, type="point_of_interest")
    return places

def ingest(lat, lng, radius):
    init_db()
    venues = fetch_eventbrite_venues(lat, lng, radius)
    if not venues:
        logger.warning("No venues found from Eventbrite; exiting.")
        return

    rows = []
    for vlat, vlng in venues:
        logger.info(f"Fetching Google Popular Times at {vlat:.4f},{vlng:.4f}")
        try:
            places = fetch_google_populartimes(vlat, vlng, radius)
        except Exception as e:
            logger.error(f"Google Places error: {e}")
            continue

        for p in places:
            pid = p.get("place_id")
            name = p.get("name")
            pt = p.get("populartimes")
            live = None
            try:
                live = get_live_populartimes(GOOGLE_API_KEY, pid)
            except Exception:
                pass

            rows.append((pid, name, p.get("lat"), p.get("lng"), f"SRID=4326;POINT({p.get('lng')} {p.get('lat')})", pt, live))

    if not rows:
        logger.warning("No popular times data collected; exiting.")
        return

    with get_db_conn() as conn:
        with conn.cursor() as cur:
            # Upsert to avoid duplicates
            execute_values(cur, """
                INSERT INTO crowd_popularity
                  (place_id, name, lat, lng, location, popular_times, live_populartimes)
                VALUES %s
                ON CONFLICT (place_id) DO UPDATE SET
                  name = EXCLUDED.name,
                  lat = EXCLUDED.lat,
                  lng = EXCLUDED.lng,
                  location = EXCLUDED.location,
                  popular_times = EXCLUDED.popular_times,
                  live_populartimes = EXCLUDED.live_populartimes,
                  retrieved_at = NOW()
            """, rows)
        conn.commit()
    logger.info(f"Inserted/Updated {len(rows)} records into crowd_popularity.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 crowd_ingestion.py LATITUDE LONGITUDE [RADIUS_METERS]")
        print(f"Default radius (meters): {DEFAULT_RADIUS}")
        sys.exit(1)

    lat = float(sys.argv[1])
    lng = float(sys.argv[2])
    radius = int(sys.argv[3]) if len(sys.argv) >= 4 else DEFAULT_RADIUS

    ingest(lat, lng, radius)
