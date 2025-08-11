def compute_area_density(df):
    """
    Compute a simple crowd density metric: average live popularity of all venues.
    """
    density = df["live_popularity"].dropna().mean()
    return density
