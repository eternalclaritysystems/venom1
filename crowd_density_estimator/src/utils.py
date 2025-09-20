
# src/utils.py
import yaml
from pathlib import Path


def load_config(filepath):
    """Load YAML config file."""
    with open(filepath, "r") as f:
        return yaml.safe_load(f)


def ensure_dirs(config):
    """
    Ensure that all necessary directories exist
    based on the config file.
    """
    paths = [
        config["outputs"]["processed_csv"],
        config["outputs"]["map_html"],
    ]

    for p in paths:
        parent = Path(p).parent
        parent.mkdir(parents=True, exist_ok=True)
