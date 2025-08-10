#!/usr/bin/env python3
"""
crowd_ingestion.py

Ingests crowd-popularity data for real event venues without any hard-coded locations.
Uses:
  - Eventbrite API to find live/upcoming events by city name.
  - Google Places Popular Times + Live Busyness (via populartimes & livepopulartimes).
  - PostgreSQL to store results.

REQUIREMENTS:
  pip install requests psycopg2-binary populartimes livepopulartimes

USAGE:
  export EVENTBRITE_TOKEN="…"
  export GOOGLE_API_KEY="…"
  export PG_DB="crowd_db"
  export PG_USER="postgres"
  export PG_PASS="password"
  export PG_HOST="localhost"
  export PG_PORT="5432"
  export SEARCH_RADIUS="5000m"           # e.g. "5000m", "10km"
  export CITIES="New York,Los Angeles"   # comma-separated list of city names

  python3 crowd_ingestion.py
"""

import os
import sys
import logging
import requests
import psycopg2
from psycopg2.extras import execute_values
from populartimes import get as gp_get
from livepopulartimes import get_live_populartimes
from datetime import datetime

# ─── CONFIG FROM ENV ───────────────────────────────────────────────────────────
EVENTBRITE_TOKEN = os.getenv("EVENTBRITE_TOKEN")
GOOGLE_API_KEY     = os.getenv("GOOGLE_API_KEY")
DB_CONFIG          = {
    "dbname": os.getenv("PG_DB"),
    "user":   os.getenv("PG_USER"),
    "password": os.getenv("PG_PASS"),
    "host":   os.getenv("PG_HOST"),
    "port":   os.getenv("PG_PORT"),
}
SEARCH_RADIUS      = os.getenv("SEARCH_RADIUS")  # e.g. "5000m" or "10km"
CITIES             = os.getenv("CITIES")        # e.g. "New York,Los Angeles"

# ─── BASIC VALIDATION ──────────────────────────────────────────────────────────
missing = [k for k,v in [
    ("EVENTBRITE_TOKEN", EVENTBRITE_TOKEN),
    ("GOOGLE_API_KEY",   GOOGLE_API_KEY),
    ("PG_DB",            DB_CONFIG["dbname"]),
    ("PG_USER",          DB_CONFIG["user"]),
    ("PG_PASS",          DB_CONFIG["password"]),
    ("PG_HOST",          DB_CONFIG["host"]),
    ("PG_PORT",          DB_CONFIG["port"]),
    ("SEARCH_RADIUS",    SEARCH_RADIUS),
    ("CITIES",           CITIES),
] if not v]
if missing:
    sys.stderr.write(f"Error: missing env vars: {', '.join(missing)}\n")
    sys.exit(1)

cities = [c.strip() for c in CITIES.split(",") if c.strip()]

# ─── LOGGER ────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("crowd_ingestion")

# ─── DATABASE HELPERS ──────────────────────────────────────────────────────────
def get_db_conn():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS crowd_popularity (
                    id SERIAL PRIMARY KEY,
                    place_id TEXT,
                    name TEXT,
                    lat DOUBLE PRECISION,
                    lng DOUBLE PRECISION,
                    retrieved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    popular_times JSONB,
                    live_populartimes JSONB
                );
            """)
        conn.commit()

# ─── EVENTBRITE FETCH ─────────────────────────────────────────────────────────
def fetch_eventbrite_venues(city_name):
    """
    Fetches up to 50 upcoming Eventbrite events in this city,
    and returns a set of (lat, lng) tuples for their venues.
    """
    headers = {"Authorization": f"Bearer {EVENTBRITE_TOKEN}"}
    params = {
        "location.address": city_name,
        "location.within":  SEARCH_RADIUS,
        "expand":           "venue",
        "sort_by":          "date"
    }
    resp = requests.get("https://www.eventbriteapi.com/v3/events/search/", headers=headers, params=params)
    resp.raise_for_status()
    data = resp.json().get("events", [])
    coords = set()
    for ev in data:
        venue = ev.get("venue", {})
        lat = venue.get("latitude")
        lng = venue.get("longitude")
        if lat and lng:
            coords.add((float(lat), float(lng)))
    logger.info(f"[Eventbrite] {len(coords)} venues in “{city_name}”")
    return coords

# ─── GOOGLE POPULAR TIMES ──────────────────────────────────────────────────────
def fetch_popular_for(lat, lng):
    """
    Returns a list of places (dicts) around this lat/lng,
    each with keys: place_id, name, lat, lng, popular_times.
    """
    places = gp_get(GOOGLE_API_KEY, lat=lat, lng=lng, radius=int(SEARCH_RADIUS.rstrip("mkm")), type="point_of_interest")
    return places

# ─── INGESTION ────────────────────────────────────────────────────────────────
def ingest():
    init_db()
    rows = []
    for city in cities:
        venues = fetch_eventbrite_venues(city)
        for lat, lng in venues:
            logger.info(f"Querying Popular Times at {lat:.4f},{lng:.4f}")
            try:
                places = fetch_popular_for(lat, lng)
            except Exception as e:
                logger.error(f"  → Google Places error: {e}")
                continue

            for p in places:
                pid   = p.get("place_id")
                name  = p.get("name")
                pt    = p.get("populartimes")
                live  = None
                try:
                    live = get_live_populartimes(GOOGLE_API_KEY, pid)
                except Exception:
                    # not every place supports live data
                    pass
                rows.append((pid, name, p.get("lat"), p.get("lng"), pt, live))

    if not rows:
        logger.warning("No data collected; exiting.")
        return

    with get_db_conn() as conn:
        with conn.cursor() as cur:
            execute_values(cur, """
                INSERT INTO crowd_popularity
                  (place_id, name, lat, lng, popular_times, live_populartimes)
                VALUES %s
            """, rows)
        conn.commit()
    logger.info(f"Inserted {len(rows)} records into crowd_popularity.")

# ─── ENTRY POINT ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ingest()
