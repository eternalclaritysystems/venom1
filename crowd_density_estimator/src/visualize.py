# src/visualize.py

import folium
from folium import plugins
import webbrowser

def make_map(df, config):
    out_path = config["outputs"]["map_html"]
    center = [config["map"]["center_lat"], config["map"]["center_lon"]]

    # Create base map
    m = folium.Map(location=center, zoom_start=config["map"]["zoom"])

    # Heatmap data
    heat_data = [
        [row["lat"], row["lon"], row["count"]]
        for _, row in df.iterrows()
        if not (row["lat"] is None or row["lon"] is None)
    ]

    # Add heatmap layer
    plugins.HeatMap(
        heat_data,
        radius=config["map"]["heatmap_radius"],
        blur=15,
        max_zoom=12,
    ).add_to(m)

    # Save map
    m.save(out_path)
    print(f"[visualize] Map saved to {out_path}")

    # 🚀 Open in default browser
    webbrowser.open(out_path)
