import dash
from pathlib import Path
from dash import Dash, Input, Output, State, callback, dcc, html, callback_context
import pandas as pd
import json
from datetime import datetime
from charts.global_policies.gp_treemap_chart import (
    build_treemap_data,
    create_treemap_fig,
)
from components.excel_export import create_filtered_excel_download
from components.tabs.global_policies.gp_tab1 import create_chart_row


def preprocess_treemap_data(df):
    """
    Preprocess dataframe for treemap visualization.
    Creates stacked_df with attr_type and attr_value columns.

    Args:
        df: Raw DataFrame with policy data

    Returns:
        stacked_df: Processed DataFrame with one row per objective/instrument
    """
    # Identify the latest amendment name for each policy
    latest_metadata = df.groupby("policy_id")["version"].last().reset_index()

    # Filter original DF to only include rows matching that Policy + Amendment combo
    # This ensures we get ALL objective/instrument combinations for only the final version
    treemap_df = pd.merge(df, latest_metadata, on=["policy_id", "version"], how="inner")

    # Create a clean Objective DataFrame
    obj_long = treemap_df[treemap_df["has_objective"] == "Yes"].copy()
    obj_long = obj_long.drop_duplicates(
        subset=[
            "policy_id",
            "jurisdiction_level",
            "city",
            "county",
            "state_province",
            "country",
            "country_iso_code",
            "supranational_policy_area",
            "region",
            "order_type",
            "status",
            "objective",
        ]
    )
    obj_long["attr_type"] = "Objective"
    obj_long["attr_value"] = obj_long["objective"]

    # Create a clean Instrument DataFrame
    inst_long = treemap_df[treemap_df["has_instrument"] == "Yes"].copy()
    inst_long = inst_long.drop_duplicates(
        subset=[
            "policy_id",
            "jurisdiction_level",
            "city",
            "county",
            "state_province",
            "country",
            "country_iso_code",
            "supranational_policy_area",
            "region",
            "order_type",
            "status",
            "instrument",
        ]
    )
    inst_long["attr_type"] = "Instrument"
    inst_long["attr_value"] = inst_long["instrument"]

    # Stack instrument and objective dataframes to ensure 1 row per Objective and 1 row per Instrument
    stacked_df = pd.concat([obj_long, inst_long], ignore_index=True)

    # Calculate counts on the stacked data
    stacked_df["unique_per_attr"] = stacked_df.groupby(
        [
            "jurisdiction_level",
            "city",
            "county",
            "state_province",
            "country",
            "country_iso_code",
            "supranational_policy_area",
            "region",
            "order_type",
            "status",
            "objective",
            "attr_value",
        ],
        dropna=False,
    )["policy_id"].transform("nunique")
    stacked_df = stacked_df.drop(
        ["instrument", "has_instrument", "objective", "has_objective"], axis=1
    )
    stacked_df["deduped_policy_count"] = (~stacked_df["policy_id"].duplicated()).astype(
        int
    )

    return stacked_df


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


def register_gp_tab2_callbacks(app, df):
    # Update all filters and handle clearing
    @app.callback(
        [
            Output("gp_tab2_order_type", "options"),
            Output("gp_tab2_status", "options"),
            Output("gp_tab2_instrument", "style"),
            Output("gp_tab2_objective", "style"),
            Output(
                "gp_tab2_instrument", "options"
            ),  # Change to options to support disabled
            Output(
                "gp_tab2_objective", "options"
            ),  # Change to options to support disabled
            Output("gp_tab2_instrument", "value"),  # Clear incompatible values
            Output("gp_tab2_objective", "value"),  # Clear incompatible values
            Output("gp_tab2_order_type", "value"),  # For clear button
            Output("gp_tab2_status", "value"),  # For clear button
        ],
        [
            Input("gp_tab2_order_type", "value"),
            Input("gp_tab2_status", "value"),
            Input("gp_tab2_instrument", "value"),
            Input("gp_tab2_objective", "value"),
            Input("gp_tab2_clear-filters-btn", "n_clicks"),  # Add clear button as input
        ],
        [State("active-tab-store", "data")],
    )
    def update_filters(
        gp_tab2_order_type,
        gp_tab2_status,
        gp_tab2_instrument,
        gp_tab2_objective,
        clear_clicks,
        active_tab,
    ):
        # Only process if we're on tab-2 (allow None for initial load)
        if active_tab is not None and active_tab != "tab-2":
            raise dash.exceptions.PreventUpdate

        ctx = dash.callback_context

        # Handle clear button click
        if ctx.triggered:
            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
            if trigger_id == "gp_tab2_clear-filters-btn":
                # Return all options and cleared values using stacked_df
                stacked_df = preprocess_treemap_data(df)
                # Get all instrument and objective options (all enabled when cleared)
                all_instruments = set(
                    stacked_df[stacked_df["attr_type"] == "Instrument"]["attr_value"]
                    .dropna()
                    .unique()
                )
                all_objectives = set(
                    stacked_df[stacked_df["attr_type"] == "Objective"]["attr_value"]
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
                    get_options(stacked_df, "order_type"),
                    get_options(stacked_df, "status"),
                    {},  # Clear instrument style
                    {},  # Clear objective style
                    instrument_opts,  # All instrument options
                    objective_opts,  # All objective options
                    [],  # Clear instrument value
                    [],  # Clear objective value
                    None,  # Clear order_type value
                    None,  # Clear status value
                )

        # Preprocess data once to get stacked_df structure
        stacked_df = preprocess_treemap_data(df)

        # Order type filter: depend on previously selected filters
        order_type_df = stacked_df.copy()
        gp_tab2_order_type_opts = get_options(order_type_df, "order_type")

        status_df = stacked_df.copy()
        if gp_tab2_order_type:
            status_df = status_df[status_df["order_type"].isin(gp_tab2_order_type)]
        gp_tab2_status_opts = get_options(status_df, "status")

        # Filter stacked_df for instrument options
        instrument_df = stacked_df.copy()
        # Apply status and order_type filters
        if gp_tab2_status:
            instrument_df = instrument_df[instrument_df["status"].isin(gp_tab2_status)]
        if gp_tab2_order_type:
            instrument_df = instrument_df[
                instrument_df["order_type"].isin(gp_tab2_order_type)
            ]
        # Filter to only rows where attr_type is Instrument
        instrument_df = instrument_df[instrument_df["attr_type"] == "Instrument"]
        # Get unique instrument values that are valid for current filters
        valid_instrument_values = set(instrument_df["attr_value"].dropna().unique())

        # Get all instrument options with disabled state (use full stacked_df for all options)
        all_instrument_df = stacked_df[stacked_df["attr_type"] == "Instrument"]
        all_instruments = set(all_instrument_df["attr_value"].dropna().unique())
        gp_tab2_instrument_opts = []
        for val in sorted(all_instruments):
            if val and str(val).strip():
                gp_tab2_instrument_opts.append(
                    {
                        "label": str(val),
                        "value": val,
                        "disabled": val not in valid_instrument_values,
                    }
                )

        # Check if current instrument selections are still valid, clear if not
        if gp_tab2_instrument:
            # Filter to only keep valid selections
            gp_tab2_instrument_value = [
                v for v in gp_tab2_instrument if v in valid_instrument_values
            ]
        else:
            gp_tab2_instrument_value = []

        # Filter stacked_df for objective options
        objective_df = stacked_df.copy()
        # Apply status and order_type filters
        if gp_tab2_status:
            objective_df = objective_df[objective_df["status"].isin(gp_tab2_status)]
        if gp_tab2_order_type:
            objective_df = objective_df[
                objective_df["order_type"].isin(gp_tab2_order_type)
            ]
        # Filter to only rows where attr_type is Objective
        objective_df = objective_df[objective_df["attr_type"] == "Objective"]
        # Get unique objective values that are valid for current filters
        valid_objective_values = set(objective_df["attr_value"].dropna().unique())

        # Get all objective options with disabled state (use full stacked_df for all options)
        all_objective_df = stacked_df[stacked_df["attr_type"] == "Objective"]
        all_objectives = set(all_objective_df["attr_value"].dropna().unique())
        gp_tab2_objective_opts = []
        for val in sorted(all_objectives):
            if val and str(val).strip():
                gp_tab2_objective_opts.append(
                    {
                        "label": str(val),
                        "value": val,
                        "disabled": val not in valid_objective_values,
                    }
                )

        # Check if current objective selections are still valid, clear if not
        if gp_tab2_objective:
            # Filter to only keep valid selections
            gp_tab2_objective_value = [
                v for v in gp_tab2_objective if v in valid_objective_values
            ]
        else:
            gp_tab2_objective_value = []

        # Style outputs for instrument and objective (no special styling needed)
        gp_tab2_instrument_style = {}
        gp_tab2_objective_style = {}

        return (
            gp_tab2_order_type_opts,
            gp_tab2_status_opts,
            gp_tab2_instrument_style,
            gp_tab2_objective_style,
            gp_tab2_instrument_opts,  # Return options with disabled state
            gp_tab2_objective_opts,  # Return options with disabled state
            gp_tab2_instrument_value,  # Return cleared/validated instrument values
            gp_tab2_objective_value,  # Return cleared/validated objective values
            dash.no_update,  # Don't change order_type value
            dash.no_update,  # Don't change status value
        )

    # Update chart
    @app.callback(
        [
            Output("gp-treemap-chart-container", "children"),
            Output("gp-treemap-store", "data"),
        ],
        [
            Input("gp_tab2_apply-filters-btn", "n_clicks"),
            Input("gp_tab2_clear-filters-btn", "n_clicks"),
        ],
        [
            State("gp_tab2_order_type", "value"),
            State("gp_tab2_status", "value"),
            State("gp_tab2_instrument", "value"),
            State("gp_tab2_objective", "value"),
            State("active-tab-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def update_dashboard_on_button_click(
        apply_clicks,
        clear_clicks,
        gp_tab2_order_type,
        gp_tab2_status,
        gp_tab2_instrument,
        gp_tab2_objective,
        active_tab,
    ):
        # Only process if we're on tab-2 (allow None for initial load)
        if active_tab is not None and active_tab != "tab-2":
            raise dash.exceptions.PreventUpdate

        ctx = dash.callback_context

        if ctx.triggered:
            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

            if trigger_id == "gp_tab2_clear-filters-btn":
                # Show all data when cleared - no filters applied
                filters_applied = False

            elif trigger_id == "gp_tab2_apply-filters-btn":
                # Apply current filter states - filters will be applied inside build_treemap_data
                filters_applied = any(
                    [
                        gp_tab2_order_type,
                        gp_tab2_status,
                        gp_tab2_instrument,
                        gp_tab2_objective,
                    ]
                )
            else:
                # Initial load or other trigger
                filters_applied = False
        else:
            # Initial load - show all data
            filters_applied = False

        # Preprocess data once - creates stacked_df with attr_type and attr_value
        stacked_df = preprocess_treemap_data(df)

        # Apply filters on stacked_df (much simpler than filtering raw dataframe)
        filtered_stacked_df = stacked_df.copy()
        if gp_tab2_order_type:
            filtered_stacked_df = filtered_stacked_df[
                filtered_stacked_df["order_type"].isin(gp_tab2_order_type)
            ]
        if gp_tab2_status:
            filtered_stacked_df = filtered_stacked_df[
                filtered_stacked_df["status"].isin(gp_tab2_status)
            ]
        if gp_tab2_instrument:
            # Filter for rows where attr_type is Instrument and attr_value matches
            instrument_mask = (
                filtered_stacked_df["attr_type"] == "Instrument"
            ) & filtered_stacked_df["attr_value"].isin(gp_tab2_instrument)
            filtered_stacked_df = filtered_stacked_df[instrument_mask]
        if gp_tab2_objective:
            # Filter for rows where attr_type is Objective and attr_value matches
            objective_mask = (
                filtered_stacked_df["attr_type"] == "Objective"
            ) & filtered_stacked_df["attr_value"].isin(gp_tab2_objective)
            filtered_stacked_df = filtered_stacked_df[objective_mask]

        # Define path columns for hierarchy
        path_cols = [
            "region",
            "country",
            "jurisdiction_level",
            "state_province",
            "city",
            "attr_type",
            "attr_value",
        ]

        # Build treemap data from filtered stacked_df
        treemap_data = build_treemap_data(
            df=filtered_stacked_df,
            path_cols=path_cols,
            policy_col="policy_id",
        )

        # Create the chart figure
        gp_treemap_fig = create_treemap_fig(treemap_data)

        # Create chart component using create_chart_row
        chart_id = "gp-treemap-fig"

        # Get last modified date and add to title with styling
        last_modified_date = get_gp_last_modified_date()
        if last_modified_date:
            # Create HTML title with date on new line and smaller font
            title = html.Div(
                [
                    html.Div("Data Center Policies Distribution Across Jurisdictions"),
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
            title = "Data Center Policies Distribution Across Jurisdictions"

        expand_id = "expand-gp-treemap"
        filename = "global_policies_treemap"

        # Store treemap data for policy modal callback
        store_data = {
            "policy_ids_map": treemap_data.get("policy_ids_map", {}),
            "ids": treemap_data.get("ids", []),
            "parents": treemap_data.get("parents", []),
            "node_levels": treemap_data.get("node_levels", {}),
            "current_root": "world",  # Track current root for modal logic
        }

        return (
            html.Div(
                [
                    html.A(id="global-policies-jurisdictional-distribution-section"),
                    create_chart_row(
                        chart_id=chart_id,
                        title=title,
                        expand_id=expand_id,
                        filename=filename,
                        figure=gp_treemap_fig,
                    ),
                ],
                style={"margin": "35px 0"},
            ),
            store_data,
        )

    # Modal callback
    @app.callback(
        [
            Output("treemap-graph-modal", "is_open"),
            Output("treemap-modal-title", "children"),
            Output("treemap-expanded-graph", "figure"),
        ],
        [Input("expand-gp-treemap", "n_clicks")],
        [
            State("treemap-graph-modal", "is_open"),
            State("gp-treemap-fig", "figure"),
            State("active-tab-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def toggle_modal(expand_clicks, is_open, gp_treemap_fig, active_tab):
        # Only process if we're on tab-2 (allow None for initial load)
        if active_tab is not None and active_tab != "tab-2":
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
                    html.Div("Data Center Policies Distribution Across Jurisdictions"),
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
            modal_title = "Data Center Policies Distribution Across Jurisdictions"

        return (
            not is_open,
            modal_title,
            gp_treemap_fig or {},
        )

    # Policy details modal callback - opens when clicking on final (leaf) nodes
    @app.callback(
        [
            Output("policy-details-modal", "is_open"),
            Output("policy-details-modal-title", "children"),
            Output("policy-details-modal-subtitle", "children"),
            Output("policy-details-modal-content", "children"),
        ],
        [
            Input("gp-treemap-fig", "clickData"),
            Input("policy-details-modal-close", "n_clicks"),
        ],
        [
            State("gp-treemap-store", "data"),
            State("policy-details-modal", "is_open"),
            State("active-tab-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def toggle_policy_details_modal(
        click_data, close_clicks, treemap_store, is_open, active_tab
    ):
        """
        Handle clicks on treemap nodes.
        Only open modal when user clicks on a final attr_value leaf node
        that is already the current root (zoomed in state).
        """
        # Only process if we're on tab-2
        if active_tab is not None and active_tab != "tab-2":
            raise dash.exceptions.PreventUpdate

        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Handle close button click
        if trigger_id == "policy-details-modal-close":
            return False, "", "", ""

        # Handle treemap click
        if trigger_id == "gp-treemap-fig" and click_data:
            clicked_node_id = click_data.get("points", [{}])[0].get("id", "")

            if not clicked_node_id or not treemap_store:
                raise dash.exceptions.PreventUpdate

            # Check if this is a leaf node (no children)
            parents = treemap_store.get("parents", [])
            policy_ids_map = treemap_store.get("policy_ids_map", {})

            # A node is a leaf if no other node has it as a parent
            is_leaf = clicked_node_id not in parents

            # Check if this is a final attr_value node by looking at the path structure
            # attr_type is always "Objective" or "Instrument", and attr_value follows it
            node_parts = clicked_node_id.split("/")
            is_attr_value_level = len(node_parts) >= 3 and node_parts[-2] in [
                "Objective",
                "Instrument",
            ]

            # Only open modal if:
            # 1. It's a leaf node (no children)
            # 2. It's at the final attr_value level (parent is Objective or Instrument)
            if is_leaf and clicked_node_id in policy_ids_map and is_attr_value_level:
                # This is a final node - show policy details modal
                policy_ids = policy_ids_map.get(clicked_node_id, [])

                # Extract node path components from the ID
                # Format: world/region/country/jurisdiction_level/state_province/city/attr_type/attr_value
                node_parts = clicked_node_id.split("/")

                # Get attr_value (last segment) and attr_type (second to last)
                attr_value = node_parts[-1] if len(node_parts) > 0 else ""
                attr_type = node_parts[-2] if len(node_parts) > 1 else ""

                # Create title in format: "Attr_type: Attr_value"
                if attr_type and attr_value:
                    modal_title = f"{attr_type}: {attr_value}"
                else:
                    modal_title = attr_value or clicked_node_id

                # Build navigation path (excluding world, attr_type, attr_value)
                # Show: Region > Country > Jurisdiction > State/Province > City
                path_parts = node_parts[1:-2] if len(node_parts) > 3 else []
                navigation_path = " › ".join(path_parts) if path_parts else ""

                # Build policy table content
                policy_rows = []
                for policy_id in policy_ids:
                    # Get policy metadata from the original dataframe
                    policy_data = df[df["policy_id"] == policy_id]
                    if not policy_data.empty:
                        row = policy_data.iloc[0]
                        order_type = (
                            row.get("order_type", "N/A")
                            if pd.notna(row.get("order_type"))
                            else "N/A"
                        )
                        status = (
                            row.get("status", "N/A")
                            if pd.notna(row.get("status"))
                            else "N/A"
                        )
                        jurisdiction = (
                            row.get("jurisdiction_level", "N/A")
                            if pd.notna(row.get("jurisdiction_level"))
                            else "N/A"
                        )
                        country = (
                            row.get("country", "N/A")
                            if pd.notna(row.get("country"))
                            else "N/A"
                        )

                        policy_rows.append(
                            html.Tr(
                                [
                                    html.Td(policy_id, style={"fontWeight": "500"}),
                                    html.Td(order_type),
                                    html.Td(status),
                                    html.Td(jurisdiction),
                                    html.Td(country),
                                ]
                            )
                        )
                    else:
                        policy_rows.append(
                            html.Tr(
                                [
                                    html.Td(policy_id, style={"fontWeight": "500"}),
                                    html.Td("N/A"),
                                    html.Td("N/A"),
                                    html.Td("N/A"),
                                    html.Td("N/A"),
                                ]
                            )
                        )

                # Create table header style
                th_style = {
                    "textAlign": "left",
                    "padding": "10px 12px",
                    "borderBottom": "2px solid #dee2e6",
                    "backgroundColor": "#f8f9fa",
                    "fontWeight": "600",
                    "fontSize": "0.85rem",
                    "color": "#495057",
                }

                # Create table content
                content = html.Div(
                    [
                        # Policy count badge
                        html.Div(
                            [
                                html.Span(
                                    f"{len(policy_ids)} ",
                                    style={
                                        "fontWeight": "600",
                                        "fontSize": "1.1rem",
                                        "color": "#2c7a7b",
                                    },
                                ),
                                html.Span(
                                    "policies found",
                                    style={"color": "#666", "fontSize": "0.95rem"},
                                ),
                            ],
                            style={"marginBottom": "20px"},
                        ),
                        # Policy table
                        html.Table(
                            [
                                html.Thead(
                                    html.Tr(
                                        [
                                            html.Th("Policy ID", style=th_style),
                                            html.Th("Order Type", style=th_style),
                                            html.Th("Status", style=th_style),
                                            html.Th("Jurisdiction", style=th_style),
                                            html.Th("Country", style=th_style),
                                        ]
                                    )
                                ),
                                html.Tbody(policy_rows, style={"fontSize": "0.9rem"}),
                            ],
                            style={
                                "width": "100%",
                                "borderCollapse": "collapse",
                                "border": "1px solid #dee2e6",
                                "borderRadius": "8px",
                                "overflow": "hidden",
                            },
                            className="policy-details-table",
                        ),
                    ]
                )

                return True, modal_title, navigation_path, content
            else:
                # Not a leaf node - let treemap handle navigation
                raise dash.exceptions.PreventUpdate

        raise dash.exceptions.PreventUpdate

    @app.callback(
        Output("download-gp-treemap-fig", "data"),
        Input("download-btn-gp-treemap-fig", "n_clicks"),
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


# def register_gp_tab2_callbacks(app, df):
#     @app.callback(
#     Output('treemap', 'figure'),
#     [Input('apply-filters-btn', 'n_clicks')],
#     [State('filter-dropdown', 'value'), ...],
# )

#     def update_treemap(n_clicks, filter_value):
#             # Filter the dataframe based on filter inputs
#         filtered_df = filtered_df.copy()

#             # Define path columns for hierarchy
#         path_cols = [
#                 "region",
#                 "country",
#                 "jurisdiction_level",
#                 "state_province",
#                 "city",
#                 "attr_type",
#                 "attr_value",
#             ]
#         # Build treemap data from filtered dataframe
#         treemap_data = build_treemap_data(df=filtered_df, path_cols=path_cols, policy_col="policy_id")

#         # Create and return the chart
#         fig = create_treemap_fig(treemap_data)
#         return fig
#     #
#     # For interactive click handling:
#     @callback(Output('treemap', 'figure'), Input('treemap', 'clickData'), State('store', 'data'))
#     def on_click(click_data, data):
#         if click_data and click_data['points'][0]['id'] in data['policy_ids_map']:
#             return create_treemap_fig(data, show_policies_for=click_data['points'][0]['id'])
#         return create_treemap_fig(data)
