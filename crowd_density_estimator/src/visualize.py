# src/visualize.py
import math
import requests
import folium
from folium.plugins import HeatMap, MarkerCluster

def _haversine(lat1, lon1, lat2, lon2):
    """
    Haversine distance in kilometers between two points.
    """
    R = 6371.0  # Earth radius km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2.0)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def _get_ip_location(timeout=3):
    """
    Try to get approximate user location via IP geolocation.
    Uses ip-api.com (no key). Returns dict with 'lat','lon','city' on success or None.
    """
    try:
        resp = requests.get("http://ip-api.com/json", params={"fields":"status,lat,lon,city"}, timeout=timeout)
        if resp.status_code != 200:
            return None
        data = resp.json()
        if data.get("status") != "success":
            return None
        return {"lat": float(data.get("lat")), "lon": float(data.get("lon")), "city": data.get("city", "")}
    except Exception:
        return None

def make_map(df, config):
    """
    Create a Folium heatmap with clustered popups and small circle markers.
    Auto-centers on the nearest event to your current IP location if possible.
    Fallbacks:
      - median of events if IP geolocation unavailable
      - country-wide default if no events
    """
    # Map fallback defaults
    default_center_lat = config.get("map", {}).get("center_lat", 40.7128)
    default_center_lon = config.get("map", {}).get("center_lon", -74.0060)
    default_zoom = config.get("map", {}).get("zoom", 12)
    heatmap_radius = config.get("map", {}).get("heatmap_radius", 25)
    out_path = config.get("outputs", {}).get("map_html", "outputs/map.html")

    # Determine center and zoom
    center_lat, center_lon, zoom = default_center_lat, default_center_lon, default_zoom

    # Attempt IP geolocation
    ip_loc = _get_ip_location()
    if ip_loc is not None and df is not None and not df.empty:
        # find nearest density cell to user's location
        user_lat, user_lon = ip_loc["lat"], ip_loc["lon"]
        # compute distances to each row and pick minimum
        min_row = None
        min_dist = float("inf")
        for _, row in df.iterrows():
            try:
                d = _haversine(user_lat, user_lon, float(row["lat"]), float(row["lon"]))
            except Exception:
                continue
            if d < min_dist:
                min_dist = d
                min_row = row
        if min_row is not None:
            center_lat = float(min_row["lat"])
            center_lon = float(min_row["lon"])
            zoom = max(10, default_zoom)  # closer zoom when centering near user
        else:
            # no valid rows; center on user's location but zoom out a bit
            center_lat, center_lon = user_lat, user_lon
            zoom = 10
    elif df is not None and not df.empty:
        # No IP info; center on median of event density
        center_lat = float(df["lat"].median())
        center_lon = float(df["lon"].median())
        zoom = default_zoom
    else:
        # No events, no IP: default to country-wide view (USA center)
        center_lat, center_lon = 39.8283, -98.5795
        zoom = 4

    # Build map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom)

    # Prepare heatmap data (lat, lon, weight)
    heat_data = []
    for _, row in (df.iterrows() if (df is not None and not df.empty) else []):
        try:
            lat = float(row["lat"])
            lon = float(row["lon"])
            weight = float(row.get("count", 1))
            heat_data.append([lat, lon, weight])
        except Exception:
            continue

    if heat_data:
        HeatMap(heat_data, radius=heatmap_radius, blur=15, max_zoom=12).add_to(m)

    # Marker cluster + small circle markers, with popups & optional tooltip
    if df is not None and not df.empty:
        cluster = MarkerCluster().add_to(m)
        for _, row in df.iterrows():
            try:
                lat = float(row["lat"])
                lon = float(row["lon"])
            except Exception:
                continue

            popup_text = row.get("event_names") if "event_names" in row.index else None
            if not popup_text:
                # fallback to count
                popup_text = f"Count: {row.get('count', 0)}"

            # add small visible circle marker
            folium.CircleMarker(
                location=[lat, lon],
                radius=4,
                color="#2A7AE2",
                fill=True,
                fill_color="#2A7AE2",
                fill_opacity=0.8,
                weight=0.5,
                popup=folium.Popup(popup_text, max_width=300)
            ).add_to(m)

            # add cluster marker (clickable) so users can zoom/click clustered items
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(cluster)

    # Save and open
    m.save(out_path)
    print(f"[visualize] Map saved to {out_path}")
    try:
        import webbrowser
        webbrowser.open(out_path)
    except Exception:
        pass
