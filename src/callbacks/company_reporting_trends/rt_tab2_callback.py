import dash
from pathlib import Path
from dash import Input, Output, State, html
import json
from datetime import datetime
from charts.energy_reporting_heatmap import create_energy_reporting_heatmap
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


def register_rt_tab2_callbacks(app, df):
    """Register callbacks for RT Tab 2 (energy reporting barchart).

    Filters are inside each tab. Filter values are synced via rt-filter-store
    so that switching tabs preserves the user's selections.
    """

    # Callback to update chart when filters or tab changes
    @app.callback(
        Output("rt-fig2-container", "children"),
        [
            Input(f"{ID_PREFIX}filter-store", "data"),
            Input(f"{ID_PREFIX}active-tab-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def update_rt_tab2_chart(filter_data, active_tab):
        """Update the timeline barchart based on filter selections from store"""
        # Only process if we're on tab-2 (allow None for initial load)
        if active_tab is not None and active_tab != "tab-2":
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
        rt_tab2_fig = create_energy_reporting_heatmap(filtered_df)

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
            title = "Energy Reporting by Company Over Time"

        return html.Div(
            [
                html.A(id="rt-tab2-nav"),
                create_figure_card(
                    fig_id="rt-tab2-fig1",
                    title=title,
                    expand_id="expand-rt-tab2-fig1",
                    filename="reporting_trends_barchart",
                    figure=rt_tab2_fig,
                ),
            ],
            style={"margin": "35px 0"},
        )

    # NOTE: Filter sync callbacks (sync_filters_to_store, sync_store_to_filters)
    # are shared across tabs and are defined in rt_tab1_callback.py only
    # to avoid duplicate output errors.

    # Modal expand callback
    @app.callback(
        [
            Output("rt-fig2-modal", "is_open"),
            Output("rt-fig2-modal-title", "children"),
            Output("rt-fig2-expanded", "figure"),
        ],
        [Input("expand-rt-tab2-fig1", "n_clicks")],
        [
            State("rt-fig2-modal", "is_open"),
            State("rt-tab2-fig1", "figure"),
        ],
        prevent_initial_call=True,
    )
    def toggle_rt_tab2_modal(expand_clicks, is_open, current_figure):
        """Toggle the expanded modal view"""
        if not expand_clicks:
            raise dash.exceptions.PreventUpdate

        # Get last modified date for modal title
        last_modified_date = get_rt_last_modified_date()
        if last_modified_date:
            modal_title = html.Div(
                [
                    html.Div("Energy Reporting by Company Over Time"),
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
            modal_title = "Energy Reporting by Company Over Time"

        return (
            not is_open,
            modal_title,
            current_figure or {},
        )

    # Download data callback
    @app.callback(
        Output("download-rt-tab2-fig1", "data"),
        Input("download-btn-rt-tab2-fig1", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_rt_tab2_data(n_clicks):
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
