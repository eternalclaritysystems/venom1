#!/usr/bin/env python3
"""
analysis_main.py

Runs the full analysis pipeline:
1. Load raw crowd data from PostgreSQL (crowd_popularity table).
2. Clean data (fix formats, remove nulls, normalize times).
3. Run tracking/detection for trends & anomalies.
4. Compute metrics (crowd_index, trend).
5. Store results in `crowd_metrics` table for API consumption.

REQUIRES:
    pip install psycopg2-binary
"""

import os
import psycopg2
from datetime import datetime, timezone
from cleaning_module import clean_data
from tracking_module import detect_trends
from metrics_module import compute_metrics

# ─── CONFIG ───────────────────────────────────────────────────────────────────
DB_CONFIG = {
    "dbname": os.getenv("PG_DB"),
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASS"),
    "host": os.getenv("PG_HOST"),
    "port": os.getenv("PG_PORT"),
}

# ─── DB HELPERS ───────────────────────────────────────────────────────────────
def get_db_conn():
    return psycopg2.connect(**DB_CONFIG)

def init_metrics_table():
    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS crowd_metrics (
                    id SERIAL PRIMARY KEY,
                    place_id TEXT UNIQUE,
                    place_name TEXT,
                    lat DOUBLE PRECISION,
                    lng DOUBLE PRECISION,
                    current_crowd INT,
                    trend TEXT,
                    crowd_index DOUBLE PRECISION,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
        conn.commit()

# ─── MAIN PIPELINE ────────────────────────────────────────────────────────────
def run_analysis():
    init_metrics_table()

    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT place_id, name, lat, lng, popular_times, live_populartimes
                FROM crowd_popularity;
            """)
            raw_data = cur.fetchall()

    # Step 1: Clean Data
    cleaned = clean_data(raw_data)

    # Step 2: Detect Trends
    tracked = detect_trends(cleaned)

    # Step 3: Compute Metrics
    final_results = compute_metrics(tracked)

    # Step 4: Store in `crowd_metrics`
    with get_db_conn() as conn:
        with conn.cursor() as cur:
            for r in final_results:
                cur.execute("""
                    INSERT INTO crowd_metrics
                      (place_id, place_name, lat, lng, current_crowd, trend, crowd_index, updated_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (place_id) DO UPDATE
                    SET place_name = EXCLUDED.place_name,
                        lat = EXCLUDED.lat,
                        lng = EXCLUDED.lng,
                        current_crowd = EXCLUDED.current_crowd,
                        trend = EXCLUDED.trend,
                        crowd_index = EXCLUDED.crowd_index,
                        updated_at = EXCLUDED.updated_at;
                """, (
                    r["place_id"], r["place_name"], r["lat"], r["lng"],
                    r["current_crowd"], r["trend"], r["crowd_index"],
                    datetime.now(timezone.utc)
                ))
        conn.commit()

    print(f"Analysis complete — {len(final_results)} metrics stored.")

# ─── ENTRY POINT ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    run_analysis()
