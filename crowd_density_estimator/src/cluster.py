# src/cluster.py
import pandas as pd
from sklearn.cluster import DBSCAN

def cluster_points(df: pd.DataFrame, eps=0.01, min_samples=3) -> pd.DataFrame:
    """Cluster lat/lon points using DBSCAN."""
    coords = df[["lat", "lon"]].to_numpy()
    db = DBSCAN(eps=eps, min_samples=min_samples, metric="haversine").fit(coords)
    df["cluster"] = db.labels_
    return df
