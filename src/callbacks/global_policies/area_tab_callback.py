import dash
from pathlib import Path
from dash import Dash, Input, Output, State, callback, dcc, html, callback_context
import pandas as pd
from charts.global_policies.stacked_area_chart import (
    create_global_policies_stacked_area_plot,
)
from components.excel_export import create_filtered_excel_download
from components.tabs.global_policies.stacked_area_tab import create_chart_row


def apply_multi_value_filter(df, column, selected_values):
    """Helper function to apply multi-value string matching filter"""
    if not selected_values:
        return df

    mask = pd.Series([False] * len(df), index=df.index)
    for value in selected_values:
        mask = mask | df[column].str.contains(value, case=False, na=False, regex=False)
    return df[mask]


def get_multi_value_options(df, column):
    """Extract unique values from multi-value fields"""
    all_values = set()
    for value_str in df[column].dropna().unique():
        values = [v.strip() for v in str(value_str).split(",")]
        all_values.update(values)
    return [{"label": val, "value": val} for val in sorted(all_values) if val]


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


def filter_data(
    df,
    gp_jurisdiction_level,
    gp_region,
    gp_country,
    gp_state_province,
    gp_county,
    gp_city,
    gp_order_type,
    gp_status,
    gp_instrument,
    gp_objective,
):
    """Filter dataframe based on all selections"""
    filtered_df = df.copy()

    # Standard single-value filters
    if gp_jurisdiction_level:
        filtered_df = filtered_df[
            filtered_df["jurisdiction_level"].isin(gp_jurisdiction_level)
        ]
    if gp_order_type:
        filtered_df = filtered_df[filtered_df["order_type"].isin(gp_order_type)]
    if gp_status:
        filtered_df = filtered_df[filtered_df["status"].isin(gp_status)]

    # Multi-value location fields (using apply_multi_value_filter if available, or simple isin)
    if gp_region:
        filtered_df = filtered_df[filtered_df["region"].isin(gp_region)]
    if gp_country:
        filtered_df = filtered_df[filtered_df["country"].isin(gp_country)]
    if gp_state_province:
        filtered_df = filtered_df[filtered_df["state_province"].isin(gp_state_province)]
    if gp_county:
        filtered_df = filtered_df[filtered_df["county"].isin(gp_county)]
    if gp_city:
        filtered_df = filtered_df[filtered_df["city"].isin(gp_city)]

    # Instrument and Objective filters - need to check both the column value AND has_instrument/has_objective
    # Since data is pivoted, we need to get policy_ids that match, then filter the full dataframe
    matching_policy_ids = None

    if gp_instrument:
        # Filter to rows where instrument matches AND has_instrument value "yes"
        # Convert has_instrument to string and check for truthy values
        has_instrument_true = (
            (filtered_df["has_instrument"] == True)
            | (filtered_df["has_instrument"] == 1)
            | (
                filtered_df["has_instrument"]
                .astype(str)
                .str.upper()
                .isin(["YES", "TRUE", "1"])
            )
        )
        instrument_mask = (
            filtered_df["instrument"].isin(gp_instrument) & has_instrument_true
        )
        # Get unique policy_ids that match the instrument filter
        matching_policy_ids = set(filtered_df[instrument_mask]["policy_id"].unique())

    if gp_objective:
        # Filter to rows where objective matches AND has_objective indicates "yes"
        has_objective_true = (
            (filtered_df["has_objective"] == True)
            | (filtered_df["has_objective"] == 1)
            | (
                filtered_df["has_objective"]
                .astype(str)
                .str.upper()
                .isin(["YES", "TRUE", "1"])
            )
        )
        objective_mask = (
            filtered_df["objective"].isin(gp_objective) & has_objective_true
        )
        # Get unique policy_ids that match the objective filter
        objective_policy_ids = set(filtered_df[objective_mask]["policy_id"].unique())

        # If instrument filter was also applied, intersect the sets (policies must match BOTH)
        # Otherwise, just use the objective policy_ids
        if matching_policy_ids is not None:
            matching_policy_ids = matching_policy_ids & objective_policy_ids
        else:
            matching_policy_ids = objective_policy_ids

    # Apply the policy_id filter if instrument or objective filters were used
    if matching_policy_ids is not None:
        filtered_df = filtered_df[filtered_df["policy_id"].isin(matching_policy_ids)]

    # # Multi-value address fields
    # filtered_df = apply_multi_value_filter(filtered_df, "region", region)
    # filtered_df = apply_multi_value_filter(filtered_df, "country", country)
    # filtered_df = apply_multi_value_filter(filtered_df, "state_province", state)
    # filtered_df = apply_multi_value_filter(filtered_df, "county", county)
    # filtered_df = apply_multi_value_filter(filtered_df, "city", city)

    return filtered_df


def register_global_policies_area_callbacks(app, df):
    # Update all filters and handle clearing
    @app.callback(
        [
            Output("gp_jurisdiction_level", "options"),
            Output("gp_region", "options"),
            Output("gp_country", "options"),
            Output("gp_state_province", "options"),
            Output("gp_county", "options"),
            Output("gp_city", "options"),
            Output("gp_order_type", "options"),
            Output("gp_status", "options"),
            Output("gp_instrument", "style"),
            Output("gp_objective", "style"),
            Output("gp_instrument", "options"),  # Change to options to support disabled
            Output("gp_objective", "options"),  # Change to options to support disabled
            Output("gp_instrument", "value"),  # Clear incompatible values
            Output("gp_objective", "value"),  # Clear incompatible values
            Output("gp_jurisdiction_level", "value"),  # For clear button
            Output("gp_region", "value"),  # For clear button
            Output("gp_country", "value"),  # For clear button
            Output("gp_state_province", "value"),  # For clear button
            Output("gp_county", "value"),  # For clear button
            Output("gp_city", "value"),  # For clear button
            Output("gp_order_type", "value"),  # For clear button
            Output("gp_status", "value"),  # For clear button
        ],
        [
            Input("gp_jurisdiction_level", "value"),
            Input("gp_region", "value"),
            Input("gp_country", "value"),
            Input("gp_state_province", "value"),
            Input("gp_county", "value"),
            Input("gp_city", "value"),
            Input("gp_order_type", "value"),
            Input("gp_status", "value"),
            Input("gp_instrument", "value"),
            Input("gp_objective", "value"),
            Input("gp_clear-filters-btn", "n_clicks"),  # Add clear button as input
        ],
    )
    def update_filters(
        gp_jurisdiction_level,
        gp_region,
        gp_country,
        gp_state_province,
        gp_county,
        gp_city,
        gp_order_type,
        gp_status,
        gp_instrument,
        gp_objective,
        clear_clicks,
    ):
        ctx = dash.callback_context

        # Handle clear button click
        if ctx.triggered:
            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
            if trigger_id == "gp_clear-filters-btn":
                # Return all options and cleared values
                base_df = df.copy()
                # For clear, show all instruments/objectives as enabled
                # Create filtered dataframes with all instruments/objectives available
                all_instrument_df = base_df[
                    (base_df["has_instrument"] == True)
                    | (base_df["has_instrument"] == 1)
                    | (
                        base_df["has_instrument"]
                        .astype(str)
                        .str.upper()
                        .isin(["YES", "TRUE", "1"])
                    )
                ]
                all_objective_df = base_df[
                    (base_df["has_objective"] == True)
                    | (base_df["has_objective"] == 1)
                    | (
                        base_df["has_objective"]
                        .astype(str)
                        .str.upper()
                        .isin(["YES", "TRUE", "1"])
                    )
                ]
                return (
                    [
                        {"label": str(val), "value": val}
                        for val in sorted(
                            base_df["jurisdiction_level"].dropna().unique()
                        )
                    ],
                    get_multi_value_options(base_df, "region"),
                    get_multi_value_options(base_df, "country"),
                    get_multi_value_options(base_df, "state_province"),
                    get_multi_value_options(base_df, "county"),
                    get_multi_value_options(base_df, "city"),
                    get_multi_value_options(base_df, "order_type"),
                    get_multi_value_options(base_df, "status"),
                    {},
                    {},
                    # Get all instrument/objective options (all enabled when cleared)
                    _get_instrument_options_with_disabled(df, all_instrument_df),
                    _get_objective_options_with_disabled(df, all_objective_df),
                    [],  # Clear instrument
                    [],  # Clear objective
                    None,  # Clear jurisdiction_level
                    None,  # Clear region
                    None,  # Clear country
                    None,  # Clear state_province
                    None,  # Clear county
                    None,  # Clear city
                    None,  # Clear order_type
                    None,  # Clear status
                )

        # Start with full data for each filter's options
        base_df = df.copy()

        # Jurisdiction level options (no dependencies)
        gp_jurisdiction_level_opts = [
            {"label": str(val), "value": val}
            for val in sorted(base_df["jurisdiction_level"].dropna().unique())
        ]

        # Apply jurisdiction level filter first to all subsequent filters
        if gp_jurisdiction_level:
            base_df = base_df[base_df["jurisdiction_level"].isin(gp_jurisdiction_level)]

        # Location filters: depend on jurisdiction level + higher level locations
        region_df = base_df.copy()
        gp_region_opts = get_multi_value_options(region_df, "region")

        country_df = base_df.copy()
        country_df = apply_multi_value_filter(country_df, "region", gp_region)
        gp_country_opts = get_multi_value_options(country_df, "country")

        state_df = base_df.copy()
        state_df = apply_multi_value_filter(state_df, "region", gp_region)
        state_df = apply_multi_value_filter(state_df, "country", gp_country)
        gp_state_province_opts = get_multi_value_options(state_df, "state_province")

        county_df = base_df.copy()
        county_df = apply_multi_value_filter(county_df, "region", gp_region)
        county_df = apply_multi_value_filter(county_df, "country", gp_country)
        county_df = apply_multi_value_filter(
            county_df, "state_province", gp_state_province
        )
        gp_county_opts = get_multi_value_options(county_df, "county")

        city_df = base_df.copy()
        city_df = apply_multi_value_filter(city_df, "region", gp_region)
        city_df = apply_multi_value_filter(city_df, "country", gp_country)
        city_df = apply_multi_value_filter(city_df, "state_province", gp_state_province)
        city_df = apply_multi_value_filter(city_df, "county", gp_county)
        gp_city_opts = get_multi_value_options(city_df, "city")

        # Order type filter: depend on previously selected filters
        order_type_df = base_df.copy()
        # Apply all location filters to climate data
        order_type_df = apply_multi_value_filter(order_type_df, "region", gp_region)
        order_type_df = apply_multi_value_filter(order_type_df, "country", gp_country)
        order_type_df = apply_multi_value_filter(
            order_type_df, "state_province", gp_state_province
        )
        order_type_df = apply_multi_value_filter(order_type_df, "county", gp_county)
        order_type_df = apply_multi_value_filter(order_type_df, "city", gp_city)
        gp_order_type_opts = get_multi_value_options(order_type_df, "order_type")

        status_df = base_df.copy()
        # Apply all location filters to climate data
        status_df = apply_multi_value_filter(status_df, "region", gp_region)
        status_df = apply_multi_value_filter(status_df, "country", gp_country)
        status_df = apply_multi_value_filter(
            status_df, "state_province", gp_state_province
        )
        status_df = apply_multi_value_filter(status_df, "county", gp_county)
        status_df = apply_multi_value_filter(status_df, "city", gp_city)
        gp_status_opts = get_multi_value_options(status_df, "status")

        instrument_df = base_df.copy()
        # Apply jurisdiction level filter first
        if gp_jurisdiction_level:
            instrument_df = instrument_df[
                instrument_df["jurisdiction_level"].isin(gp_jurisdiction_level)
            ]
        # Apply status and order_type filters (single-value filters, use .isin())
        if gp_status:
            instrument_df = instrument_df[instrument_df["status"].isin(gp_status)]
        if gp_order_type:
            instrument_df = instrument_df[
                instrument_df["order_type"].isin(gp_order_type)
            ]
        # Apply location filters
        if gp_region:
            instrument_df = instrument_df[instrument_df["region"].isin(gp_region)]
        if gp_country:
            instrument_df = instrument_df[instrument_df["country"].isin(gp_country)]
        if gp_state_province:
            instrument_df = instrument_df[
                instrument_df["state_province"].isin(gp_state_province)
            ]
        if gp_county:
            instrument_df = instrument_df[instrument_df["county"].isin(gp_county)]
        if gp_city:
            instrument_df = instrument_df[instrument_df["city"].isin(gp_city)]
        # Filter to only rows where has_instrument is True/Yes/1
        has_instrument_true = (
            (instrument_df["has_instrument"] == True)
            | (instrument_df["has_instrument"] == 1)
            | (
                instrument_df["has_instrument"]
                .astype(str)
                .str.upper()
                .isin(["YES", "TRUE", "1"])
            )
        )
        instrument_df = instrument_df[has_instrument_true]
        # Get unique instrument values that are valid for current filters
        valid_instrument_values = set(instrument_df["instrument"].dropna().unique())

        # Get all instrument options with disabled state
        gp_instrument_opts = _get_instrument_options_with_disabled(df, instrument_df)

        # Check if current instrument selections are still valid, clear if not
        if gp_instrument:
            # Filter to only keep valid selections
            gp_instrument_value = [
                v for v in gp_instrument if v in valid_instrument_values
            ]
        else:
            gp_instrument_value = []

        objective_df = base_df.copy()
        # Apply jurisdiction level filter first
        if gp_jurisdiction_level:
            objective_df = objective_df[
                objective_df["jurisdiction_level"].isin(gp_jurisdiction_level)
            ]
        # Apply status and order_type filters (single-value filters, use .isin())
        if gp_status:
            objective_df = objective_df[objective_df["status"].isin(gp_status)]
        if gp_order_type:
            objective_df = objective_df[objective_df["order_type"].isin(gp_order_type)]
        # Apply location filters
        if gp_region:
            objective_df = objective_df[objective_df["region"].isin(gp_region)]
        if gp_country:
            objective_df = objective_df[objective_df["country"].isin(gp_country)]
        if gp_state_province:
            objective_df = objective_df[
                objective_df["state_province"].isin(gp_state_province)
            ]
        if gp_county:
            objective_df = objective_df[objective_df["county"].isin(gp_county)]
        if gp_city:
            objective_df = objective_df[objective_df["city"].isin(gp_city)]
        # Filter to only rows where has_objective is True/Yes/1
        has_objective_true = (
            (objective_df["has_objective"] == True)
            | (objective_df["has_objective"] == 1)
            | (
                objective_df["has_objective"]
                .astype(str)
                .str.upper()
                .isin(["YES", "TRUE", "1"])
            )
        )
        objective_df = objective_df[has_objective_true]
        # Get unique objective values that are valid for current filters
        valid_objective_values = set(objective_df["objective"].dropna().unique())

        # Get all objective options with disabled state
        gp_objective_opts = _get_objective_options_with_disabled(df, objective_df)

        # Check if current objective selections are still valid, clear if not
        if gp_objective:
            # Filter to only keep valid selections
            gp_objective_value = [
                v for v in gp_objective if v in valid_objective_values
            ]
        else:
            gp_objective_value = []

        # Style outputs for instrument and objective (no special styling needed)
        gp_instrument_style = {}
        gp_objective_style = {}

        return (
            gp_jurisdiction_level_opts,
            gp_region_opts,
            gp_country_opts,
            gp_state_province_opts,
            gp_county_opts,
            gp_city_opts,
            gp_order_type_opts,
            gp_status_opts,
            gp_instrument_style,
            gp_objective_style,
            gp_instrument_opts,  # Return options with disabled state
            gp_objective_opts,  # Return options with disabled state
            gp_instrument_value,  # Return cleared/validated instrument values
            gp_objective_value,  # Return cleared/validated objective values
            dash.no_update,  # Don't change jurisdiction_level value
            dash.no_update,  # Don't change region value
            dash.no_update,  # Don't change country value
            dash.no_update,  # Don't change state_province value
            dash.no_update,  # Don't change county value
            dash.no_update,  # Don't change city value
            dash.no_update,  # Don't change order_type value
            dash.no_update,  # Don't change status value
        )

    # Update chart
    @app.callback(
        Output("gp-chart-container", "children"),
        [
            Input("gp_apply-filters-btn", "n_clicks"),
            Input("gp_clear-filters-btn", "n_clicks"),
        ],
        [
            State("gp_jurisdiction_level", "value"),
            State("gp_region", "value"),
            State("gp_country", "value"),
            State("gp_state_province", "value"),
            State("gp_county", "value"),
            State("gp_city", "value"),
            State("gp_order_type", "value"),
            State("gp_status", "value"),
            State("gp_instrument", "value"),
            State("gp_objective", "value"),
        ],
        prevent_initial_call=False,
    )
    def update_dashboard_on_button_click(
        apply_clicks,
        clear_clicks,
        gp_jurisdiction_level,
        gp_region,
        gp_country,
        gp_state_province,
        gp_county,
        gp_city,
        gp_order_type,
        gp_status,
        gp_instrument,
        gp_objective,
    ):
        ctx = dash.callback_context

        if ctx.triggered:
            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

            if trigger_id == "gp_clear-filters-btn":
                # Show all data when cleared
                filtered_df = df.copy()
                filters_applied = False

            elif trigger_id == "gp_apply-filters-btn":
                # Apply current filter states
                filtered_df = filter_data(
                    df,
                    gp_jurisdiction_level,
                    gp_region,
                    gp_country,
                    gp_state_province,
                    gp_county,
                    gp_city,
                    gp_order_type,
                    gp_status,
                    gp_instrument,
                    gp_objective,
                )
                filters_applied = any(
                    [
                        gp_jurisdiction_level,
                        gp_region,
                        gp_country,
                        gp_state_province,
                        gp_county,
                        gp_city,
                        gp_order_type,
                        gp_status,
                        gp_instrument,
                        gp_objective,
                    ]
                )
            else:
                # Initial load or other trigger
                filtered_df = df.copy()
                filters_applied = False
        else:
            # Initial load - show all data
            filtered_df = df.copy()
            filters_applied = False

        # Create the chart figure
        gp_stacked_area_fig = create_global_policies_stacked_area_plot(
            filtered_df=filtered_df,
            full_df=df,
            filters_applied=filters_applied,
        )

        # Create chart component using create_chart_row
        chart_id = "gp-stacked-area-chart"
        title = "Cumulative Number of Policies Across Jurisdictions Over Time"
        expand_id = "expand-gp-stacked-area"
        filename = "global_policies_stacked_area"

        return html.Div(
            [
                html.A(id="global-policies-cumulative-trends-section"),
                create_chart_row(
                    chart_id=chart_id,
                    title=title,
                    expand_id=expand_id,
                    filename=filename,
                    figure=gp_stacked_area_fig,
                ),
            ],
            style={"margin": "35px 0"},
        )

    # Modal callback
    @app.callback(
        [
            Output("stacked-area-graph-modal", "is_open"),
            Output("stacked-area-modal-title", "children"),
            Output("stacked-area-expanded-graph", "figure"),
        ],
        [Input("expand-gp-stacked-area", "n_clicks")],
        [
            State("stacked-area-graph-modal", "is_open"),
            State("gp-stacked-area-chart", "figure"),
        ],
        prevent_initial_call=True,
    )
    def toggle_modal(expand_clicks, is_open, gp_stacked_area_fig):
        # Only open modal when button is clicked
        if not expand_clicks:
            raise dash.exceptions.PreventUpdate

        return (
            not is_open,
            "Cumulative Number of Policies Across Jurisdictions Over Time - Expanded View",
            gp_stacked_area_fig or {},
        )

    @app.callback(
        Output("download-gp-stacked-area-chart", "data"),
        Input("download-btn-gp-stacked-area-chart", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_gp_data(n_clicks):
        # Get the project root directory (2 levels up from callbacks directory)
        root_dir = Path(__file__).parent.parent.parent
        input_path = root_dir / "data" / "DCEWM-GlobalPolicies.xlsx"

        # Debug print
        print(f"Looking for file at: {input_path}")
        print(f"File exists: {input_path.exists()}")

        return create_filtered_excel_download(
            input_path=input_path,
            output_filename="global_policies_data.xlsx",
            sheets_to_export=[
                "Policy_Eval",
                "Read Me",
            ],
            internal_prefix="_internal_",
            # skip_rows=1,
            n_clicks=n_clicks,
        )
