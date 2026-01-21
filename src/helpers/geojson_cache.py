"""
Helper to cache GeoJSON file locally to avoid runtime network dependencies.
"""

import json
from pathlib import Path
import urllib.request

# Get absolute path to data/dependencies folder
_script_dir = Path(__file__).parent
_project_root = _script_dir.parent.parent
GEOJSON_CACHE_FILE = (
    _project_root / "data" / "dependencies" / "ne_50m_admin_1_states_provinces.geojson"
)
GEOJSON_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_1_states_provinces.geojson"


def download_geojson():
    """Download GeoJSON file and save to data/dependencies folder."""
    try:
        print(f"Downloading GeoJSON from {GEOJSON_URL}...")
        with urllib.request.urlopen(GEOJSON_URL, timeout=10) as response:
            geojson_data = response.read().decode("utf-8")

        # Ensure data/dependencies directory exists
        GEOJSON_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Save to file
        with open(GEOJSON_CACHE_FILE, "w") as f:
            f.write(geojson_data)

        print(f"GeoJSON saved to {GEOJSON_CACHE_FILE}")
        return True
    except Exception as e:
        print(f"Error downloading GeoJSON: {e}")
        return False


def load_geojson():
    """
    Load GeoJSON from local cache file.

    Returns:
        GeoJSON dict if file exists, None otherwise.
    """
    if GEOJSON_CACHE_FILE.exists():
        try:
            with open(GEOJSON_CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading cached GeoJSON: {e}")
            return None
    else:
        return None


def get_geojson():
    """
    Get GeoJSON data - tries local cache first, falls back to URL if needed.

    Returns:
        GeoJSON dict if available, or URL string as fallback.
    """
    geojson_data = load_geojson()
    if geojson_data:
        return geojson_data
    else:
        # Fallback to URL if cache doesn't exist
        print(f"Warning: GeoJSON cache not found, using URL (may be slower)")
        return GEOJSON_URL
