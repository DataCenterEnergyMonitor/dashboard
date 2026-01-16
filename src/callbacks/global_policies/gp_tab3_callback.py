import os
import dash
from pathlib import Path
from dash import Input, Output, State, html
import pandas as pd
import json
from datetime import datetime
from charts.global_policies.gp_choropleth_map import (
    create_gp_choropleth_map,
)
from components.excel_export import create_filtered_excel_download
from components.tabs.global_policies.gp_tab3 import create_chart_row
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import numpy as np

CACHE_FILE = "location_coords_cache3.csv"
geojson_url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_1_states_provinces.geojson"

# Initialize geocoder once outside the function to avoid repeated overhead
geolocator = Nominatim(user_agent="dcewm_v0")
geocode_service = RateLimiter(geolocator.geocode, min_delay_seconds=1)


def geocode_with_level(
    df, level="city", city_col="city", state_col="state_province", country_col="country"
):
    df_clean = df.copy()

    if level == "state":
        geo_cols = [state_col, country_col]
        lat_name, lon_name = "state_lat", "state_lon"
    else:
        geo_cols = [city_col, state_col, country_col]
        lat_name, lon_name = "lat", "lon"

    available_cols = [c for c in geo_cols if c in df_clean.columns]

    # standardize data types and handle "empty" strings
    for col in available_cols:
        df_clean[col] = (
            df_clean[col]
            .astype(str)
            .replace(["nan", "None", "", "<NA>", "NONE", "nan", "null"], pd.NA)
        )

    # only process rows where the level-specific primary column is NOT NA
    # level='state' -> check state_col | level='city' -> check city_col
    mask = df_clean[available_cols[0]].notna()
    process_df = df_clean[mask].copy()
    other_df = df_clean[~mask].copy()

    if process_df.empty:
        # ensure columns exist even if we skip processing
        for col in [lat_name, lon_name]:
            if col not in df_clean.columns:
                df_clean[col] = pd.NA
        return df_clean

    unique_locs = process_df[available_cols].drop_duplicates()

    # load cache
    if os.path.exists(CACHE_FILE):
        cache = pd.read_csv(CACHE_FILE, dtype=str)
    else:
        cache = pd.DataFrame(
            columns=[city_col, state_col, country_col, "lat", "lon", "geo_level"]
        )

    level_cache = cache[cache["geo_level"] == level].copy()

    # identify locations with missing coords
    merged = unique_locs.merge(
        level_cache, on=available_cols, how="left", indicator=True
    )
    to_geocode = merged[merged["_merge"] == "left_only"][available_cols]

    if not to_geocode.empty:
        print(f"Geocoding {len(to_geocode)} new {level} locations...")
        new_results = []
        for _, row in to_geocode.iterrows():
            # Filter out NA parts for the query string
            address_parts = [str(row[c]) for c in available_cols if pd.notna(row[c])]
            address = ", ".join(address_parts)

            try:
                location = geocode_service(address)
                if location:
                    res = {col: row[col] for col in available_cols}
                    res.update(
                        {
                            "lat": str(location.latitude),
                            "lon": str(location.longitude),
                            "geo_level": level,
                        }
                    )
                    new_results.append(res)
            except Exception as e:
                print(f"    Error on {address}: {e}")

        if new_results:
            new_df = pd.DataFrame(new_results)
            cache = pd.concat([cache, new_df], ignore_index=True)
            cache.to_csv(CACHE_FILE, index=False)

    # refresh level_cache from updated cache
    updated_level_cache = cache[cache["geo_level"] == level][
        available_cols + ["lat", "lon"]
    ].copy()
    updated_level_cache = updated_level_cache.rename(
        columns={"lat": lat_name, "lon": lon_name}
    )

    # drop target columns from process_df if they exist to prevent merge duplicates
    process_df = process_df.drop(columns=[lat_name, lon_name], errors="ignore")

    # merge and recombine
    process_df = process_df.merge(updated_level_cache, on=available_cols, how="left")
    result_df = pd.concat([process_df, other_df], ignore_index=True)

    return result_df


def apply_multi_value_filter(df, column, selected_values):
    """Helper function to apply multi-value string matching filter"""
    if not selected_values:
        return df

    mask = pd.Series([False] * len(df), index=df.index)
    for value in selected_values:
        mask = mask | df[column].str.contains(value, case=False, na=False, regex=False)
    return df[mask]


# Note: filter_data function removed - filtering now happens inside build_treemap_data
# on the stacked_df which has a cleaner structure with attr_type and attr_value columns


def get_options(df, column):
    """Get unique values from a dataframe column as dropdown options"""
    if column not in df.columns:
        return []
    unique_values = df[column].dropna().unique()
    return [
        {"label": str(val), "value": val}
        for val in sorted(unique_values)
        if val is not None and str(val).strip()
    ]


def get_gp_last_modified_date():
    """Get the last modified date for DCEWM-GlobalPolicies.xlsx from metadata.json"""
    try:
        root_dir = Path(__file__).parent.parent.parent.parent
        json_path = root_dir / "data" / "metadata.json"

        if not json_path.exists():
            print(f"Warning: Metadata file not found at {json_path.absolute()}")
            return None

        with open(json_path, "r") as f:
            metadata = json.load(f)

        # Find the GlobalPolicies file entry
        for file_info in metadata.get("files", []):
            if file_info.get("source_file") == "DCEWM-GlobalPolicies.xlsx":
                last_modified = file_info.get("last_modified")
                if last_modified:
                    # Parse ISO format date and format as "Month Day, Year"
                    dt = datetime.fromisoformat(last_modified)
                    return dt.strftime("%B %d, %Y")

        print("Warning: DCEWM-GlobalPolicies.xlsx not found in metadata")
        return None
    except (FileNotFoundError, KeyError, ValueError) as e:
        # If metadata file doesn't exist or parsing fails, return None
        print(f"Warning: Could not load last modified date: {e}")
        import traceback

        traceback.print_exc()
        return None


def _get_instrument_options_with_disabled(full_df, filtered_df):
    """Get all instrument options with disabled state for items not in filtered data"""
    # Get all possible instrument values from full dataset (where has_instrument is True)
    full_has_instrument_true = (
        (full_df["has_instrument"] == True)
        | (full_df["has_instrument"] == 1)
        | (full_df["has_instrument"].astype(str).str.upper().isin(["YES", "TRUE", "1"]))
    )
    all_instruments = set(
        full_df[full_has_instrument_true]["instrument"].dropna().unique()
    )

    # Get available instrument values from filtered dataset
    available_instruments = set(filtered_df["instrument"].dropna().unique())

    # Create options with disabled state
    options = []
    for val in sorted(all_instruments):
        if val and str(val).strip():
            options.append(
                {
                    "label": str(val),
                    "value": val,
                    "disabled": val
                    not in available_instruments,  # Disable if not available
                }
            )
    return options


def _get_objective_options_with_disabled(full_df, filtered_df):
    """Get all objective options with disabled state for items not in filtered data"""
    # Get all possible objective values from full dataset (where has_objective is True)
    full_has_objective_true = (
        (full_df["has_objective"] == True)
        | (full_df["has_objective"] == 1)
        | (full_df["has_objective"].astype(str).str.upper().isin(["YES", "TRUE", "1"]))
    )
    all_objectives = set(
        full_df[full_has_objective_true]["objective"].dropna().unique()
    )

    # Get available objective values from filtered dataset
    available_objectives = set(filtered_df["objective"].dropna().unique())

    # Create options with disabled state
    options = []
    for val in sorted(all_objectives):
        if val and str(val).strip():
            options.append(
                {
                    "label": str(val),
                    "value": val,
                    "disabled": val
                    not in available_objectives,  # Disable if not available
                }
            )
    return options


def register_gp_tab3_callbacks(app, df):
    # Update all filters and handle clearing
    @app.callback(
        [
            Output("gp_tab3_jurisdiction_level", "options"),
            Output("gp_tab3_order_type", "options"),
            Output("gp_tab3_status", "options"),
            Output("gp_tab3_instrument", "style"),
            Output("gp_tab3_objective", "style"),
            Output(
                "gp_tab3_instrument", "options"
            ),  # Change to options to support disabled
            Output(
                "gp_tab3_objective", "options"
            ),  # Change to options to support disabled
            Output("gp_tab3_instrument", "value"),  # Clear incompatible values
            Output("gp_tab3_objective", "value"),  # Clear incompatible values
            Output("gp_tab3_jurisdiction_level", "value"),  # For clear button
            Output("gp_tab3_order_type", "value"),  # For clear button
            Output("gp_tab3_status", "value"),  # For clear button
        ],
        [
            Input("gp_tab3_jurisdiction_level", "value"),
            Input("gp_tab3_order_type", "value"),
            Input("gp_tab3_status", "value"),
            Input("gp_tab3_instrument", "value"),
            Input("gp_tab3_objective", "value"),
            Input("gp_tab3_clear-filters-btn", "n_clicks"),  # Add clear button as input
        ],
        [State("active-tab-store", "data")],
    )
    def update_filters(
        gp_tab3_jurisdiction_level,
        gp_tab3_order_type,
        gp_tab3_status,
        gp_tab3_instrument,
        gp_tab3_objective,
        clear_clicks,
        active_tab,
    ):
        # Only process if we're on tab-3 (allow None for initial load)
        if active_tab is not None and active_tab != "tab-3":
            raise dash.exceptions.PreventUpdate

        ctx = dash.callback_context

        # Handle clear button click
        if ctx.triggered:
            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
            if trigger_id == "gp_tab3_clear-filters-btn":
                # Return all options and cleared values using map_df
                map_df = df.copy()
                # Get all instrument and objective options (all enabled when cleared)
                all_instruments = set(
                    map_df[map_df["attr_type"] == "Instrument"]["attr_value"]
                    .dropna()
                    .unique()
                )
                all_objectives = set(
                    map_df[map_df["attr_type"] == "Objective"]["attr_value"]
                    .dropna()
                    .unique()
                )
                instrument_opts = [
                    {"label": str(val), "value": val, "disabled": False}
                    for val in sorted(all_instruments)
                    if val and str(val).strip()
                ]
                objective_opts = [
                    {"label": str(val), "value": val, "disabled": False}
                    for val in sorted(all_objectives)
                    if val and str(val).strip()
                ]
                return (
                    get_options(map_df, "jurisdiction_level"),
                    get_options(map_df, "order_type"),
                    get_options(map_df, "status"),
                    {},  # Clear instrument style
                    {},  # Clear objective style
                    instrument_opts,  # All instrument options
                    objective_opts,  # All objective options
                    [],  # Clear instrument value
                    [],  # Clear objective value
                    None,  # Clear jurisdiction_level value
                    None,  # Clear order_type value
                    None,  # Clear status value
                )

        # Preprocess data once to get map_df structure
        map_df = df.copy()
        # calculate total policies count per region
        map_df["unique_per_country"] = map_df.groupby(
            [
                "country",
                "country_iso_code",
            ],
            dropna=False,
        )["deduped_policy_count"].transform("sum")

        map_df["unique_per_state"] = map_df.groupby(
            ["country", "country_iso_code", "state_iso_code"],
            dropna=False,
        )["deduped_policy_count"].transform("sum")

        city_policy_sum = map_df.groupby(
            ["country", "country_iso_code", "state_iso_code", "city"],
            dropna=False,
        )["deduped_policy_count"].transform("sum")

        # Add total count per city to the rows where city is not empty/null
        map_df["unique_per_city"] = np.where(
            (map_df["city"].notna()) & (map_df["city"] != ""), city_policy_sum, np.nan
        )

        # Jurisdiction level filter: no dependencies
        jurisdiction_level_df = map_df.copy()
        gp_tab3_jurisdiction_level_opts = get_options(
            jurisdiction_level_df, "jurisdiction_level"
        )

        # Order type filter: depend on previously selected filters
        order_type_df = map_df.copy()
        if gp_tab3_jurisdiction_level and gp_tab3_jurisdiction_level_opts:
            order_type_df = order_type_df[
                order_type_df["jurisdiction_level"].isin(gp_tab3_jurisdiction_level)
            ]
        gp_tab3_order_type_opts = get_options(order_type_df, "order_type")

        status_df = map_df.copy()
        if gp_tab3_order_type:
            status_df = status_df[status_df["order_type"].isin(gp_tab3_order_type)]
        gp_tab3_status_opts = get_options(status_df, "status")

        # Filter map_df for instrument options
        instrument_df = map_df.copy()
        # Apply status and order_type filters
        if gp_tab3_jurisdiction_level:
            instrument_df = instrument_df[
                instrument_df["jurisdiction_level"].isin(gp_tab3_jurisdiction_level)
            ]
        if gp_tab3_status:
            instrument_df = instrument_df[instrument_df["status"].isin(gp_tab3_status)]
        if gp_tab3_order_type:
            instrument_df = instrument_df[
                instrument_df["order_type"].isin(gp_tab3_order_type)
            ]
        # Filter to only rows where attr_type is Instrument
        instrument_df = instrument_df[instrument_df["attr_type"] == "Instrument"]
        # Get unique instrument values that are valid for current filters
        valid_instrument_values = set(instrument_df["attr_value"].dropna().unique())

        # Get all instrument options with disabled state (use full map_df for all options)
        all_instrument_df = map_df[map_df["attr_type"] == "Instrument"]
        all_instruments = set(all_instrument_df["attr_value"].dropna().unique())
        gp_tab3_instrument_opts = []
        for val in sorted(all_instruments):
            if val and str(val).strip():
                gp_tab3_instrument_opts.append(
                    {
                        "label": str(val),
                        "value": val,
                        "disabled": val not in valid_instrument_values,
                    }
                )

        # Check if current instrument selections are still valid, clear if not
        if gp_tab3_instrument:
            # Filter to only keep valid selections
            gp_tab3_instrument_value = [
                v for v in gp_tab3_instrument if v in valid_instrument_values
            ]
        else:
            gp_tab3_instrument_value = []

        # Filter map_df for objective options
        objective_df = map_df.copy()
        # Apply status and order_type filters
        if gp_tab3_jurisdiction_level:
            objective_df = objective_df[
                objective_df["jurisdiction_level"].isin(gp_tab3_jurisdiction_level)
            ]
        if gp_tab3_status:
            objective_df = objective_df[objective_df["status"].isin(gp_tab3_status)]
        if gp_tab3_order_type:
            objective_df = objective_df[
                objective_df["order_type"].isin(gp_tab3_order_type)
            ]
        # Filter to only rows where attr_type is Objective
        objective_df = objective_df[objective_df["attr_type"] == "Objective"]
        # Get unique objective values that are valid for current filters
        valid_objective_values = set(objective_df["attr_value"].dropna().unique())

        # Get all objective options with disabled state (use full map_df for all options)
        all_objective_df = map_df[map_df["attr_type"] == "Objective"]
        all_objectives = set(all_objective_df["attr_value"].dropna().unique())
        gp_tab3_objective_opts = []
        for val in sorted(all_objectives):
            if val and str(val).strip():
                gp_tab3_objective_opts.append(
                    {
                        "label": str(val),
                        "value": val,
                        "disabled": val not in valid_objective_values,
                    }
                )

        # Check if current objective selections are still valid, clear if not
        if gp_tab3_objective:
            # Filter to only keep valid selections
            gp_tab3_objective_value = [
                v for v in gp_tab3_objective if v in valid_objective_values
            ]
        else:
            gp_tab3_objective_value = []

        # Style outputs for instrument and objective (no special styling needed)
        gp_tab3_instrument_style = {}
        gp_tab3_objective_style = {}

        return (
            gp_tab3_jurisdiction_level_opts,
            gp_tab3_order_type_opts,
            gp_tab3_status_opts,
            gp_tab3_instrument_style,
            gp_tab3_objective_style,
            gp_tab3_instrument_opts,  # Return options with disabled state
            gp_tab3_objective_opts,  # Return options with disabled state
            gp_tab3_instrument_value,  # Return cleared/validated instrument values
            gp_tab3_objective_value,  # Return cleared/validated objective values
            dash.no_update,  # Don't change jurisdiction_level value
            dash.no_update,  # Don't change order_type value
            dash.no_update,  # Don't change status value
        )

    # Update chart
    @app.callback(
        [
            Output("gp-map-container", "children"),
        ],
        [
            Input("gp_tab3_apply-filters-btn", "n_clicks"),
            Input("gp_tab3_clear-filters-btn", "n_clicks"),
        ],
        [
            State("gp_tab3_jurisdiction_level", "value"),
            State("gp_tab3_order_type", "value"),
            State("gp_tab3_status", "value"),
            State("gp_tab3_instrument", "value"),
            State("gp_tab3_objective", "value"),
            State("active-tab-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def update_dashboard_on_button_click(
        apply_clicks,
        clear_clicks,
        gp_tab3_jurisdiction_level,
        gp_tab3_order_type,
        gp_tab3_status,
        gp_tab3_instrument,
        gp_tab3_objective,
        active_tab,
    ):
        # Only process if we're on tab-3 (allow None for initial load)
        if active_tab is not None and active_tab != "tab-3":
            raise dash.exceptions.PreventUpdate

        ctx = dash.callback_context

        if ctx.triggered:
            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

            if trigger_id == "gp_tab3_clear-filters-btn":
                # Show all data when cleared - no filters applied
                filters_applied = False

            elif trigger_id == "gp_tab3_apply-filters-btn":
                # Apply current filter states - filters will be applied inside build_treemap_data
                filters_applied = any(
                    [
                        gp_tab3_jurisdiction_level,
                        gp_tab3_order_type,
                        gp_tab3_status,
                        gp_tab3_instrument,
                        gp_tab3_objective,
                    ]
                )
            else:
                # Initial load or other trigger
                filters_applied = False
        else:
            # Initial load - show all data
            filters_applied = False

        # Preprocess data once
        map_df = df.copy()

        # Apply filters
        filtered_map_df = map_df.copy()
        if gp_tab3_jurisdiction_level:
            filtered_map_df = filtered_map_df[
                filtered_map_df["jurisdiction_level"].isin(gp_tab3_jurisdiction_level)
            ]
        if gp_tab3_order_type:
            filtered_map_df = filtered_map_df[
                filtered_map_df["order_type"].isin(gp_tab3_order_type)
            ]
        if gp_tab3_status:
            filtered_map_df = filtered_map_df[
                filtered_map_df["status"].isin(gp_tab3_status)
            ]
        if gp_tab3_instrument:
            # Filter for rows where attr_type is Instrument and attr_value matches
            instrument_mask = (
                filtered_map_df["attr_type"] == "Instrument"
            ) & filtered_map_df["attr_value"].isin(gp_tab3_instrument)
            filtered_map_df = filtered_map_df[instrument_mask]
        if gp_tab3_objective:
            # Filter for rows where attr_type is Objective and attr_value matches
            objective_mask = (
                filtered_map_df["attr_type"] == "Objective"
            ) & filtered_map_df["attr_value"].isin(gp_tab3_objective)
            filtered_map_df = filtered_map_df[objective_mask]

        map_geo_df = filtered_map_df.copy()
        map_geo_df["lat"] = np.nan
        map_geo_df["lon"] = np.nan
        map_geo_df["state_lat"] = np.nan
        map_geo_df["state_lon"] = np.nan

        # get state centroids
        map_geo_df = geocode_with_level(
            map_geo_df, level="state", state_col="state_province", country_col="country"
        )

        # get city coordinates
        map_geo_df = geocode_with_level(
            map_geo_df,
            level="city",
            city_col="city",
            state_col="state_province",
            country_col="country",
        )

        # Calculate unique policy counts per geographic level for filtered data
        # This needs to be done on both dataframes before passing to chart
        # Calculate on filtered_map_df first (used for country-level choropleth)
        filtered_map_df["unique_per_country"] = filtered_map_df.groupby(
            ["country", "country_iso_code"],
            dropna=False,
        )["deduped_policy_count"].transform("sum")

        filtered_map_df["unique_per_state"] = filtered_map_df.groupby(
            ["country", "country_iso_code", "state_iso_code"],
            dropna=False,
        )["deduped_policy_count"].transform("sum")

        city_policy_sum = filtered_map_df.groupby(
            ["country", "country_iso_code", "state_iso_code", "city"],
            dropna=False,
        )["deduped_policy_count"].transform("sum")

        # Add total count per city to the rows where city is not empty/null
        filtered_map_df["unique_per_city"] = np.where(
            (filtered_map_df["city"].notna()) & (filtered_map_df["city"] != ""),
            city_policy_sum,
            np.nan,
        )

        # Calculate on map_geo_df as well (used for bubble locations and sizes)
        # Since map_geo_df is a copy of filtered_map_df, we can safely copy the calculated columns
        # But to be safe, recalculate to ensure alignment after geocoding
        map_geo_df["unique_per_country"] = map_geo_df.groupby(
            ["country", "country_iso_code"],
            dropna=False,
        )["deduped_policy_count"].transform("sum")

        map_geo_df["unique_per_state"] = map_geo_df.groupby(
            ["country", "country_iso_code", "state_iso_code"],
            dropna=False,
        )["deduped_policy_count"].transform("sum")

        city_policy_sum_geo = map_geo_df.groupby(
            ["country", "country_iso_code", "state_iso_code", "city"],
            dropna=False,
        )["deduped_policy_count"].transform("sum")

        map_geo_df["unique_per_city"] = np.where(
            (map_geo_df["city"].notna()) & (map_geo_df["city"] != ""),
            city_policy_sum_geo,
            np.nan,
        )

        # Create the chart figure (pass filtered_df for policy metadata display)
        gp_choropleth_map_fig = create_gp_choropleth_map(
            filtered_df=filtered_map_df,
            filtered_geo_df=map_geo_df,
            geojson_url=geojson_url,
        )

        # Create chart component using create_chart_row
        chart_id = "gp-choropleth-map-fig"

        # Get last modified date and add to title with styling
        last_modified_date = get_gp_last_modified_date()
        if last_modified_date:
            # Create HTML title with date on new line and smaller font
            title = html.Div(
                [
                    html.Div("Geographic Distribution of Data Center Policies"),
                    html.Div(
                        f"(as of {last_modified_date})",
                        style={
                            "fontSize": "0.85em",
                            "color": "#666",
                            "marginTop": "4px",
                        },
                    ),
                ]
            )
        else:
            title = "Geographic Distribution of Data Center Policies"

        expand_id = "expand-gp-choropleth-map"
        filename = "global_policies_map"

        return (
            html.Div(
                [
                    html.A(id="global-policies-geographic-distribution-section"),
                    create_chart_row(
                        chart_id=chart_id,
                        title=title,
                        expand_id=expand_id,
                        filename=filename,
                        figure=gp_choropleth_map_fig,
                    ),
                ],
                style={"margin": "35px 0"},
            ),
        )

    # Modal callback
    @app.callback(
        [
            Output("gp-map-graph-modal", "is_open"),
            Output("gp-map-modal-title", "children"),
            Output("gp-map-expanded-graph", "figure"),
        ],
        [Input("expand-gp-choropleth-map", "n_clicks")],
        [
            State("gp-map-graph-modal", "is_open"),
            State("gp-choropleth-map-fig", "figure"),
            State("active-tab-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def toggle_modal(expand_clicks, is_open, gp_choropleth_map_fig, active_tab):
        # Only process if we're on tab-3 (allow None for initial load)
        if active_tab is not None and active_tab != "tab-3":
            raise dash.exceptions.PreventUpdate
        # Only open modal when button is clicked
        if not expand_clicks:
            raise dash.exceptions.PreventUpdate

        # Get last modified date for modal title
        last_modified_date = get_gp_last_modified_date()
        if last_modified_date:
            # Create HTML modal title with date on new line and smaller font
            modal_title = html.Div(
                [
                    html.Div("Geographic Distribution of Data Center Policies"),
                    html.Div(
                        f"(as of {last_modified_date})",
                        style={
                            "fontSize": "0.85em",
                            "color": "#666",
                            "marginTop": "4px",
                        },
                    ),
                ]
            )
        else:
            modal_title = "Geographic Distribution of Data Center Policies"

        return (
            not is_open,
            modal_title,
            gp_choropleth_map_fig or {},
        )
