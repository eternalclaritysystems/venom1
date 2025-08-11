import numpy as np

def extract_crowd_metrics(df):
    """
    Extract numeric crowd levels from popular_times and live_populartimes.
    Create columns:
      - avg_popularity (average historical popularity %)
      - live_popularity (current live popularity %, if available)
    """
    avg_popularity = []
    live_popularity = []

    for _, row in df.iterrows():
        pt = row.get("popular_times") or []
        try:
            hours = []
            for day in pt:
                hours.extend([h[1] for h in day.get("data", []) if isinstance(h[1], (int, float))])
            avg_pop = np.mean(hours) if hours else np.nan
        except Exception:
            avg_pop = np.nan
        avg_popularity.append(avg_pop)

        live = row.get("live_populartimes")
        try:
            live_pop = live.get("current_popularity") if live else np.nan
        except Exception:
            live_pop = np.nan
        live_popularity.append(live_pop)

    df["avg_popularity"] = avg_popularity
    df["live_popularity"] = live_popularity
    return df

def detect_spikes(df, threshold=30):
    """
    Detect places where live popularity spikes significantly above historical average.
    Returns a DataFrame of spike places.
    """
    df["popularity_diff"] = df["live_popularity"] - df["avg_popularity"]
    spikes = df[(df["popularity_diff"] >= threshold)]
    return spikes
