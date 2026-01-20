"""
Geocoding utility functions for location coordinates.

This module handles geocoding of locations and caching of coordinates.
"""

from pathlib import Path
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable, GeocoderTimedOut

# Get absolute path to cache file (in data/dependencies folder)
_script_dir = Path(__file__).parent
_project_root = _script_dir.parent.parent
CACHE_FILE = _project_root / "data" / "dependencies" / "location_coords_cache.csv"

# Initialize geocoder once
geolocator = Nominatim(user_agent="dcewm_v0", timeout=5)
geocode_service = RateLimiter(geolocator.geocode, min_delay_seconds=1)


def load_cache(cache_file=None):
    """Load geocoding cache from file."""
    cache_path = cache_file or CACHE_FILE

    if cache_path.exists():
        return pd.read_csv(cache_path, dtype=str)
    else:
        return pd.DataFrame(
            columns=["city", "state_province", "country", "lat", "lon", "geo_level"]
        )


def save_cache(cache, cache_file=None):
    """Save geocoding cache to file."""
    cache_path = cache_file or CACHE_FILE
    cache.to_csv(cache_path, index=False)


def geocode_address(address):
    """Geocode a single address. Returns (lat, lon) or None."""
    try:
        location = geocode_service(address, timeout=5)
        if location:
            return (location.latitude, location.longitude)
    except (GeocoderUnavailable, GeocoderTimedOut, Exception):
        pass
    return None


def add_coordinates_from_cache(
    df, level="city", city_col="city", state_col="state_province", country_col="country"
):
    """
    Add coordinates to dataframe from cache only (no geocoding).

    This is the read-only version for use in callbacks.
    """
    df_clean = df.copy()

    # Determine column names based on level
    if level == "state":
        geo_cols = [state_col, country_col]
        lat_name, lon_name = "state_lat", "state_lon"
    else:
        geo_cols = [city_col, state_col, country_col]
        lat_name, lon_name = "lat", "lon"

    available_cols = [c for c in geo_cols if c in df_clean.columns]
    if not available_cols:
        # Add empty coordinate columns
        df_clean[lat_name] = pd.NA
        df_clean[lon_name] = pd.NA
        return df_clean

    # Clean up data types
    for col in available_cols:
        df_clean[col] = (
            df_clean[col]
            .astype(str)
            .replace(["nan", "None", "", "<NA>", "NONE", "null"], pd.NA)
        )

    # Process rows with valid location data
    mask = df_clean[available_cols[0]].notna()
    process_df = df_clean[mask].copy()
    other_df = df_clean[~mask].copy()

    if process_df.empty:
        df_clean[lat_name] = pd.NA
        df_clean[lon_name] = pd.NA
        return df_clean

    # Load cache and merge coordinates
    cache = load_cache()
    level_cache = cache[cache["geo_level"] == level].copy()

    if not level_cache.empty:
        level_cache_subset = level_cache[available_cols + ["lat", "lon"]].copy()
        level_cache_subset = level_cache_subset.rename(
            columns={"lat": lat_name, "lon": lon_name}
        )
        process_df = process_df.drop(columns=[lat_name, lon_name], errors="ignore")
        process_df = process_df.merge(level_cache_subset, on=available_cols, how="left")
    else:
        process_df[lat_name] = pd.NA
        process_df[lon_name] = pd.NA

    # Recombine
    result_df = pd.concat([process_df, other_df], ignore_index=True)

    # Ensure coordinate columns exist
    if lat_name not in result_df.columns:
        result_df[lat_name] = pd.NA
    if lon_name not in result_df.columns:
        result_df[lon_name] = pd.NA

    return result_df


def update_location_cache(
    df, level="city", city_col="city", state_col="state_province", country_col="country"
):
    """
    Update geocoding cache by geocoding missing locations from dataframe.

    This function makes API calls to geocode locations and should only be run:
    - During build/deployment process
    - When new data files are added
    - As a standalone script to update the cache

    This function ONLY updates the cache file - it does NOT return an updated dataframe.
    The dataframe is just used to identify which locations need geocoding.

    For app load time, use add_coordinates_from_cache() instead, which only reads
    from the existing cache file without making any API calls.
    """
    df_clean = df.copy()

    # Determine column names based on level
    if level == "state":
        geo_cols = [state_col, country_col]
        lat_name, lon_name = "state_lat", "state_lon"
    else:
        geo_cols = [city_col, state_col, country_col]
        lat_name, lon_name = "lat", "lon"

    available_cols = [c for c in geo_cols if c in df_clean.columns]
    if not available_cols:
        return  # No location columns found, nothing to geocode

    # Clean up data types
    for col in available_cols:
        df_clean[col] = (
            df_clean[col]
            .astype(str)
            .replace(["nan", "None", "", "<NA>", "NONE", "null"], pd.NA)
        )

    # Process rows with valid location data
    mask = df_clean[available_cols[0]].notna()
    process_df = df_clean[mask].copy()

    if process_df.empty:
        return  # No valid locations to process

    # Load cache
    cache = load_cache()

    # Find unique locations and check which need geocoding
    unique_locs = process_df[available_cols].drop_duplicates()
    level_cache = cache[cache["geo_level"] == level].copy()

    merged = unique_locs.merge(
        level_cache, on=available_cols, how="left", indicator=True
    )
    to_geocode = merged[merged["_merge"] == "left_only"][available_cols]

    # Geocode missing locations
    new_results = []
    if not to_geocode.empty:
        print(f"Geocoding {len(to_geocode)} new {level} locations...")
        for _, row in to_geocode.iterrows():
            address_parts = [str(row[c]) for c in available_cols if pd.notna(row[c])]
            address = ", ".join(address_parts)

            coords = geocode_address(address)
            if coords:
                res = {col: row[col] for col in available_cols}
                res.update(
                    {
                        "lat": str(coords[0]),
                        "lon": str(coords[1]),
                        "geo_level": level,
                    }
                )
                new_results.append(res)

        # Update cache with new results
        if new_results:
            new_df = pd.DataFrame(new_results)
            cache = pd.concat([cache, new_df], ignore_index=True)
            save_cache(cache)
            print(
                f"Successfully geocoded and cached {len(new_results)} {level} locations"
            )

    # Return count of newly geocoded locations (0 if none)
    return len(new_results) if new_results else 0
