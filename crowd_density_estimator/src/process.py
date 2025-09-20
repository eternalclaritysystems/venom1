# src/process.py
import pandas as pd

def calculate_density(df, config):
    """
    Produce a density DataFrame with columns:
      - lat, lon: grid cell coordinates (floored/bin)
      - count: number of events in the cell
      - event_names: short aggregated string of event names for popups

    Bins coordinates into grid using processing.lat_bin_size / lon_bin_size.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=["lat", "lon", "count", "event_names"])

    lat_bin = config.get("processing", {}).get("lat_bin_size", 0.01)
    lon_bin = config.get("processing", {}).get("lon_bin_size", 0.01)

    # compute bin (floor to bin)
    df["lat_bin"] = (df["lat"] // lat_bin) * lat_bin
    df["lon_bin"] = (df["lon"] // lon_bin) * lon_bin

    # aggregate: count + concat unique event names (short)
    def join_names(s):
        # pick up to first 5 unique names, join with " | "
        uniq = list(dict.fromkeys(s.dropna().astype(str)))  # preserves order, unique
        if not uniq:
            return ""
        if len(uniq) > 5:
            return " | ".join(uniq[:5]) + f" | +{len(uniq)-5} more"
        return " | ".join(uniq)

    grouped = (
        df.groupby(["lat_bin", "lon_bin"])
          .agg(
              count=("lat", "size"),
              event_names=("name", join_names)
          )
          .reset_index()
    )

    grouped = grouped.rename(columns={"lat_bin": "lat", "lon_bin": "lon"})
    # ensure column order
    return grouped[["lat", "lon", "count", "event_names"]]
