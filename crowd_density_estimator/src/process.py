# src/process.py

import pandas as pd

def calculate_density(df, config):
    lat_bin_size = config["processing"]["lat_bin_size"]
    lon_bin_size = config["processing"]["lon_bin_size"]

    # Bin lat/lon
    df["lat_bin"] = (df["lat"] // lat_bin_size) * lat_bin_size
    df["lon_bin"] = (df["lon"] // lon_bin_size) * lon_bin_size

    # Group and count
    grouped = (
        df.groupby(["lat_bin", "lon_bin"])
        .size()
        .reset_index(name="count")   # 👈 ensures column is called "count"
    )

    grouped.rename(columns={"lat_bin": "lat", "lon_bin": "lon"}, inplace=True)
    return grouped
