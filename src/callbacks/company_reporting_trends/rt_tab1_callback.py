import dash
from pathlib import Path
from dash import Input, Output, State, callback_context, html
import json
from datetime import datetime
from charts.reporting_barchart import create_reporting_bar_plot
from components.excel_export import create_filtered_excel_download
from components.figure_card import create_figure_card


def get_rt_last_modified_date():
    """Get the last modified date for reporting data from metadata.json"""
    try:
        root_dir = Path(__file__).parent.parent.parent.parent
        json_path = root_dir / "data" / "dependencies" / "metadata.json"

        if not json_path.exists():
            print(f"Warning: Metadata file not found at {json_path.absolute()}")
            return None

        with open(json_path, "r") as f:
            metadata = json.load(f)

        # Find the reporting file entry
        for file_info in metadata.get("files", []):
            if "reporting" in file_info.get("source_file", "").lower():
                last_modified = file_info.get("last_modified")
                if last_modified:
                    dt = datetime.fromisoformat(last_modified)
                    return dt.strftime("%B %d, %Y")

        return None
    except (FileNotFoundError, KeyError, ValueError) as e:
        print(f"Warning: Could not load last modified date: {e}")
        return None


def filter_data_by_year_range(df, from_year, to_year):
    """Filter dataframe by year range"""
    if df.empty:
        return df

    filtered_df = df.copy()

    if from_year is not None:
        filtered_df = filtered_df[filtered_df["reported_data_year"] >= from_year]

    if to_year is not None:
        filtered_df = filtered_df[filtered_df["reported_data_year"] <= to_year]

    return filtered_df


# ID prefix for this page's components
ID_PREFIX = "rt-"


def register_rt_tab1_callbacks(app, df):
    """Register callbacks for RT Tab 1 (Reporting Adoption barchart).

    Filters are inside each tab. Filter values are synced via rt-filter-store
    so that switching tabs preserves the user's selections.
    """

    # Callback to update chart when filters or tab changes
    @app.callback(
        Output("rt-fig1-container", "children"),
        [
            Input(f"{ID_PREFIX}filter-store", "data"),
            Input(f"{ID_PREFIX}active-tab-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def update_rt_tab1_chart(filter_data, active_tab):
        """Update the reporting barchart based on filter selections from store"""
        # Only process if we're on tab-1 (allow None for initial load)
        if active_tab is not None and active_tab != "tab-1":
            raise dash.exceptions.PreventUpdate

        # Get filter values from store - convert to Python int
        from_year = None
        to_year = None

        if filter_data:
            from_year = (
                int(filter_data.get("from_year"))
                if filter_data.get("from_year")
                else None
            )
            to_year = (
                int(filter_data.get("to_year")) if filter_data.get("to_year") else None
            )

        # Filter data
        filtered_df = filter_data_by_year_range(df, from_year, to_year)

        # Create the chart figure
        rt_tab1_fig = create_reporting_bar_plot(filtered_df)

        # Get last modified date for title
        last_modified_date = get_rt_last_modified_date()
        if last_modified_date:
            title = html.Div(
                [
                    html.Div("Data Center Reporting Over Time"),
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
            title = "Data Center Reporting Over Time"

        return html.Div(
            [
                html.A(id="rt-tab1-nav"),
                create_figure_card(
                    fig_id="rt-tab1-fig1",
                    title=title,
                    expand_id="expand-rt-tab1-fig1",
                    filename="reporting_trends_barchart",
                    figure=rt_tab1_fig,
                ),
            ],
            style={"margin": "35px 0"},
        )

    # Callback to sync filter component changes to the store
    # This handles year filters (all tabs), company filter (tabs 2-5), and pw_status (tabs 4-5)
    # Note: Uses pattern matching to handle optional components that may not exist on all tabs
    @app.callback(
        Output(f"{ID_PREFIX}filter-store", "data"),
        [
            Input("apply-filters-btn", "n_clicks"),
            Input("rt-clear-filters-btn", "n_clicks"),
        ],
        [
            State("rt-from-year", "value"),
            State("rt-to-year", "value"),
            State("rt-company-filter", "value"),
            State("pw_reporting_status", "value"),
            State(f"{ID_PREFIX}filter-store", "data"),
            State(f"{ID_PREFIX}active-tab-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def sync_filters_to_store(
        apply_clicks,
        clear_clicks,
        from_year,
        to_year,
        companies,
        pw_status,
        current_store,
        active_tab,
    ):
        """Sync filter component values to shared store when Apply or Clear is clicked"""
        ctx = callback_context

        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Get default pw_status values for tabs 4-5
        default_pw_status = [
            "company not established",
            "no reporting evident",
            "individual data center values only",
            "fleet-wide values only",
            "both fleet-wide and individual data center values",
            "pending",
        ]

        # Get current timestamp for cache busting
        import time

        timestamp = time.time()

        # Handle clear filters button
        if trigger_id == "rt-clear-filters-btn":
            return {
                "from_year": None,
                "to_year": None,
                "companies": None,
                "pw_status": default_pw_status
                if active_tab in ["tab-4", "tab-5"]
                else None,
                "source": "clear",
                "timestamp": timestamp,
            }

        # Handle apply filters button
        if trigger_id == "apply-filters-btn":
            return {
                "from_year": int(from_year) if from_year else None,
                "to_year": int(to_year) if to_year else None,
                "companies": companies if companies else None,
                "pw_status": pw_status if pw_status else None,
                "source": "apply",
                "timestamp": timestamp,
            }

        raise dash.exceptions.PreventUpdate

    # Modal expand callback
    @app.callback(
        [
            Output("rt-fig1-modal", "is_open"),
            Output("rt-tab1-fig1-modal-title", "children"),
            Output("rt-tab1-expanded-fig1", "figure"),
        ],
        [Input("expand-rt-tab1-fig1", "n_clicks")],
        [
            State("rt-fig1-modal", "is_open"),
            State("rt-tab1-fig1", "figure"),
        ],
        prevent_initial_call=True,
    )
    def toggle_rt_tab1_modal(expand_clicks, is_open, current_figure):
        """Toggle the expanded modal view"""
        if not expand_clicks:
            raise dash.exceptions.PreventUpdate

        # Get last modified date for modal title
        last_modified_date = get_rt_last_modified_date()
        if last_modified_date:
            modal_title = html.Div(
                [
                    html.Div("Data Center Reporting Over Time - Expanded View"),
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
            modal_title = "Data Center Reporting Over Time - Expanded View"

        return (
            not is_open,
            modal_title,
            current_figure or {},
        )

    # Download data callback
    @app.callback(
        Output("download-rt-tab1-fig1", "data"),
        Input("download-btn-rt-tab1-fig1", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_rt_tab1_data(n_clicks):
        """Download the reporting data as Excel"""
        root_dir = Path(__file__).parent.parent.parent
        input_path = root_dir / "data" / "DCEWM-Reporting.xlsx"

        return create_filtered_excel_download(
            input_path=input_path,
            output_filename="reporting_trends_data.xlsx",
            sheets_to_export=["Reporting", "Read Me"],
            internal_prefix="_internal_",
            n_clicks=n_clicks,
        )
