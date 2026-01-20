"""
Build script to update geocoding cache.

Run this script when:
- New data files are added
- New locations appear in the data
- Cache needs to be refreshed

Usage:
    python scripts/update_geocoding_cache.py
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from data_loader import load_gp_data, transpose_gp_data
from helpers.geocode_locations import update_location_cache, load_cache
from helpers.geojson_cache import download_geojson

if __name__ == "__main__":
    # Download/update GeoJSON cache
    print("Checking GeoJSON cache...")
    download_geojson()

    print("\nLoading global policies data...")
    globalpolicies_df = load_gp_data()

    print("Transposing data...")
    gp_transposed_df = transpose_gp_data(globalpolicies_df)

    print("\nUpdating geocoding cache...")
    print("Geocoding state locations...")
    new_states = update_location_cache(
        gp_transposed_df,
        level="state",
        state_col="state_province",
        country_col="country",
    )

    print("Geocoding city locations...")
    new_cities = update_location_cache(
        gp_transposed_df,
        level="city",
        city_col="city",
        state_col="state_province",
        country_col="country",
    )

    # Get total cache count
    cache = load_cache()
    total_locations = len(cache)
    new_locations = new_states + new_cities

    print("\nGeocoding cache update complete!")
    print(
        f"Added {new_locations} new location(s) ({new_states} state(s), {new_cities} city/cities)"
    )
    print(f"Total records in cache: {total_locations}")
