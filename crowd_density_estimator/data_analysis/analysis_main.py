import psycopg2
import pandas as pd
from data_cleaning import clean_data
from tracking_detection import extract_crowd_metrics, detect_spikes
from results_metrics import compute_area_density

DB_CONFIG = {
    "dbname": "crowd_db",
    "user": "postgres",
    "password": "secretpass",
    "host": "localhost",
    "port": 5432,
}

def get_db_conn():
    return psycopg2.connect(**DB_CONFIG)

def load_raw_data(since_hours=48):
    query = """
    SELECT place_id, name, lat, lng, retrieved_at, popular_times, live_populartimes
    FROM crowd_popularity
    WHERE retrieved_at >= NOW() - INTERVAL '%s hours'
    """
    with get_db_conn() as conn:
        df = pd.read_sql(query, conn, params=(since_hours,))
    return df

def main():
    print("Loading raw data...")
    raw_df = load_raw_data()
    print(f"Loaded {len(raw_df)} records.")

    print("Cleaning data...")
    clean_df = clean_data(raw_df)

    print("Extracting crowd metrics...")
    metrics_df = extract_crowd_metrics(clean_df)

    print("Detecting spikes...")
    spikes_df = detect_spikes(metrics_df)
    print(f"Found {len(spikes_df)} spike(s).")
    if not spikes_df.empty:
        print(spikes_df[["place_id", "name", "avg_popularity", "live_popularity", "popularity_diff"]])

    print("Computing area crowd density...")
    density = compute_area_density(metrics_df)
    print(f"Average live crowd density: {density:.2f}")

if __name__ == "__main__":
    main()
