import dash
from pathlib import Path
from dash import Input, Output, State, html
import pandas as pd
import json
from datetime import datetime
from charts.global_policies.gp_treemap_chart import (
    build_treemap_data,
    create_treemap_fig,
)
from components.excel_export import create_filtered_excel_download
from components.tabs.global_policies.gp_tab1 import create_chart_row

def apply_multi_value_filter(df, column, selected_values):
    """Helper function to apply multi-value string matching filter"""
    if not selected_values:
        return df

    mask = pd.Series([False] * len(df), index=df.index)
    for value in selected_values:
        mask = mask | df[column].str.contains(value, case=False, na=False, regex=False)
    return df[mask]

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
        json_path = root_dir / "data" / "dependencies" / "metadata.json"

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
            ), 
            Output(
                "gp_tab2_objective", "options"
            ), 
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
                #stacked_df = preprocess_treemap_data(df)
                stacked_df = df.copy()
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
        # stacked_df = preprocess_treemap_data(df)
        stacked_df = df.copy()

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
        # stacked_df = preprocess_treemap_data(df)
        stacked_df = df.copy()
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

        # build treemap data from filtered stacked_df
        treemap_data = build_treemap_data(
            df=filtered_stacked_df,
            path_cols=path_cols,
            policy_col="policy_id",
        )

        # create the chart figure
        gp_treemap_fig = create_treemap_fig(treemap_data, policy_metadata_df=df)

        # create chart component
        chart_id = "gp-treemap-fig"

        # get last modified date and add to title with styling
        last_modified_date = get_gp_last_modified_date()
        if last_modified_date:
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

        # Store treemap data and policy metadata for click callback
        # Extract policy metadata for display (keep it lightweight)
        policy_metadata = {}
        for pid in df["policy_id"].unique():
            row = df[df["policy_id"] == pid].iloc[0]
            policy_metadata[pid] = {
                "order_type": row.get("order_type")
                if pd.notna(row.get("order_type"))
                else "",
                "status": row.get("status") if pd.notna(row.get("status")) else "",
            }

        store_data = {
            "policy_ids_map": treemap_data.get("policy_ids_map", {}),
            "ids": treemap_data.get("ids", []),
            "labels": treemap_data.get("labels", []),
            "original_labels": treemap_data.get("original_labels", []),
            "parents": treemap_data.get("parents", []),
            "values": treemap_data.get("values", []),
            "node_levels": treemap_data.get("node_levels", {}),
            "policy_metadata": policy_metadata,
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
        # only process if on tab-2 (allow None for initial load)
        if active_tab is not None and active_tab != "tab-2":
            raise dash.exceptions.PreventUpdate
        # only open modal when button is clicked
        if not expand_clicks:
            raise dash.exceptions.PreventUpdate

        # get last modified date for modal title
        last_modified_date = get_gp_last_modified_date()
        if last_modified_date:
            # create HTML modal title with date on new line and smaller font
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

    # callback to show policy details when clicking into a final leaf node
    # tracks expanded leaf and toggles: click leaf = expand, click again = collapse
    @app.callback(
        [
            Output("gp-treemap-fig", "figure"),
            Output("gp-treemap-expanded-leaf", "data"),
        ],
        Input("gp-treemap-fig", "clickData"),
        [
            State("gp-treemap-store", "data"),
            State("gp-treemap-fig", "figure"),
            State("gp-treemap-expanded-leaf", "data"),
            State("active-tab-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def update_treemap_on_navigation(
        click_data, treemap_store, current_figure, expanded_leaf, active_tab
    ):
        """
        Handle treemap navigation with toggle behavior:
        - Click on final leaf node: show policy details in cell, store leaf ID
        - Click same leaf again OR click non-leaf: restore clean labels, clear stored ID
        """
        import copy

        # Only process if we're on tab-2
        if active_tab is not None and active_tab != "tab-2":
            raise dash.exceptions.PreventUpdate

        if not treemap_store or not current_figure:
            raise dash.exceptions.PreventUpdate

        # Handle clickData
        if not click_data:
            raise dash.exceptions.PreventUpdate

        clicked_node_id = click_data.get("points", [{}])[0].get("id", "")
        if not clicked_node_id:
            raise dash.exceptions.PreventUpdate

        # Get data from store
        store_ids = treemap_store.get("ids", [])
        parents = treemap_store.get("parents", [])
        original_labels = treemap_store.get("labels", [])
        policy_ids_map = treemap_store.get("policy_ids_map", {})
        policy_metadata = treemap_store.get("policy_metadata", {})

        print(f"\n=== TREEMAP CLICK ===")
        print(f"Clicked: {clicked_node_id}")
        print(f"Currently expanded: {expanded_leaf}")

        # Make a copy of the figure to modify
        new_figure = copy.deepcopy(current_figure)

        # Always restore all labels to original first (clean slate)
        if "data" in new_figure and len(new_figure["data"]) > 0:
            new_figure["data"][0]["labels"] = list(original_labels)

        # Check if this is a final leaf node (attr_value level)
        node_parts = clicked_node_id.split("/")
        is_leaf = clicked_node_id not in parents
        is_final_leaf = (
            is_leaf
            and len(node_parts) >= 3
            and node_parts[-2] in ["Objective", "Instrument"]
        )

        # Toggle logic: if clicking the same leaf that's already expanded, collapse it
        if expanded_leaf and clicked_node_id == expanded_leaf:
            print(f"DEBUG: Toggling OFF (same leaf clicked again)")
            return new_figure, None

        # If not a final leaf, return clean labels and clear any expanded state
        if not is_final_leaf:
            print(f"DEBUG: Not a final leaf, clearing expanded state")
            return new_figure, None

        # Final leaf node - build policy details and update label
        policy_ids = policy_ids_map.get(clicked_node_id, [])
        if not policy_ids:
            return new_figure, None

        # Build policy details text
        policy_lines = []
        for pid in policy_ids[:15]:
            meta = policy_metadata.get(pid, {})
            order_type = meta.get("order_type", "")
            status = meta.get("status", "")
            line = f"• {pid}"
            if order_type:
                line += f" ({order_type})"
            if status:
                line += f" - {status}"
            policy_lines.append(line)

        if len(policy_ids) > 15:
            policy_lines.append(f"... +{len(policy_ids) - 15} more")

        # Build the cell content
        attr_type = node_parts[-2]
        attr_value = node_parts[-1]
        cell_content = (
            f"<b>{attr_type}: {attr_value}</b><br>"
            f"{len(policy_ids)} policies<br><br>" + "<br>".join(policy_lines)
        )

        # Update the label for the clicked node
        if clicked_node_id in store_ids:
            idx = store_ids.index(clicked_node_id)
            labels = list(new_figure["data"][0]["labels"])
            labels[idx] = cell_content
            new_figure["data"][0]["labels"] = labels
            print(f"DEBUG: Expanded leaf {clicked_node_id}")

        # Return figure with policy details and store the expanded leaf ID
        return new_figure, clicked_node_id

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
