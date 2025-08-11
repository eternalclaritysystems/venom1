import pandas as pd

def clean_data(df):
    """
    Basic cleaning:
      - Drop duplicates by place_id keeping latest
      - Remove entries with missing lat/lng or place_id
      - Normalize timestamp
    """
    df = df.drop_duplicates(subset=["place_id"], keep="last")
    df = df.dropna(subset=["place_id", "lat", "lng"])
    df["retrieved_at"] = pd.to_datetime(df["retrieved_at"])
    return df
