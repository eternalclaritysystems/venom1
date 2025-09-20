# main.py
import sys
from pathlib import Path

from src import ingest, clean, process, visualize
from src.utils import load_config, ensure_dirs


def main():
    # Always resolve config.yaml relative to this file
    base_dir = Path(__file__).parent
    config_path = base_dir / "config.yaml"
    config = load_config(config_path)

    ensure_dirs(config)

    # Read Ticketmaster API details
    api_key = config["ticketmaster"]["api_key"]
    radius = config["ticketmaster"].get("radius_miles", 30)
    days = config["ticketmaster"].get("days_ahead", 30)

    # Fetch and process data
    raw = ingest.from_ticketmaster(api_key, radius, days)
    cleaned = clean.clean_data(raw)  #  correct function name
    density_df = process.calculate_density(cleaned, config)

    # Save outputs
    density_df.to_csv(config["outputs"]["processed_csv"], index=False)
    visualize.make_map(density_df, config)

    print("[main] Done. Map and data written to outputs.")


if __name__ == "__main__":
    sys.exit(main())
