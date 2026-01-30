import dash
from pathlib import Path
from dash import Input, Output, State, callback_context, html, dcc
import json
from datetime import datetime
from charts.energy_reporting_heatmap import create_energy_reporting_heatmap
from components.excel_export import create_filtered_excel_download


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


def filter_data_by_companies(df, companies, company_col="company_name"):
    """Filter dataframe by selected companies"""
    if df.empty or not companies:
        return df
    return df[df[company_col].isin(companies)]


# ID prefix for this page's components
ID_PREFIX = "rt-"


def register_rt_tab2_callbacks(app, df, pue_wue_companies_df=None):
    """Register callbacks for RT Tab 2 (energy reporting heatmap).

    Filters are inside each tab. Filter values are synced via rt-filter-store
    so that switching tabs preserves the user's selections.
    """

    # Callback to update chart when filters or tab changes
    @app.callback(
        # Output("rt-fig2-container", "children"),
        [
            Output("rt-header-container", "children"),
            Output("rt-body-container", "children"),
        ],
        [
            Input(f"{ID_PREFIX}filter-store", "data"),
            Input(f"{ID_PREFIX}active-tab-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def update_rt_tab2_chart(filter_data, active_tab):
        """Update the energy reporting heatmap based on filter selections from store"""
        # Only process if we're on tab-2 (allow None for initial load)
        if active_tab is not None and active_tab != "tab-2":
            raise dash.exceptions.PreventUpdate

        # Get filter values from store - convert to Python int
        from_year = None
        to_year = None
        companies = None

        if filter_data:
            from_year = (
                int(filter_data.get("from_year"))
                if filter_data.get("from_year")
                else None
            )
            to_year = (
                int(filter_data.get("to_year")) if filter_data.get("to_year") else None
            )
            companies = filter_data.get("companies")

        # Filter data by year range
        filtered_df = filter_data_by_year_range(df, from_year, to_year)

        # Filter by companies if selected
        filtered_df = filter_data_by_companies(filtered_df, companies)

        # Create Header (legend and x-axis)
        header_fig = create_energy_reporting_heatmap(filtered_df, header_only=True)
        # Create Body (the actual data rows)
        body_fig = create_energy_reporting_heatmap(filtered_df, header_only=False)

        header_card = dcc.Graph(
            figure=header_fig,
            config={"displayModeBar": False, "responsive": True},
            style={"height": "120px"},  # Match the fig_height in python
        )

        body_card = dcc.Graph(
            figure=body_fig,
            config={"displayModeBar": False, "responsive": True},
            # Important: the style height here must match the calculated fig_height
            style={
                "height": f"{len(filtered_df['company_name'].unique()) * 25 + 40}px"
            },
        )

        # # Create the chart figure
        # rt_tab2_fig = create_energy_reporting_heatmap(filtered_df)

        return header_card, body_card  # html.Div(
        #     [
        #         html.A(id="rt-tab2-nav"),
        #         create_figure_card(
        #             fig_id="rt-tab2-fig1",
        #             title=title,
        #             expand_id="expand-rt-tab2-fig1",
        #             filename="reporting_trends_heatmap",
        #             figure=rt_tab2_fig,
        #             show_modebar=False,
        #         ),
        #     ],
        #     style={"margin": "35px 0"},
        # )

    # NOTE: Filter sync callbacks (sync_filters_to_store, sync_store_to_filters)
    # are shared across tabs and are defined in rt_tab1_callback.py only
    # to avoid duplicate output errors.

    # Modal expand callback
    @app.callback(
        [
            Output("rt-fig2-modal", "is_open"),
            Output("rt-fig2-modal-title", "children"),
            Output("rt-fig2-expanded", "figure"),
            Output("rt-fig2-expanded", "style"),
        ],
        [Input("expand-rt-tab2-fig1", "n_clicks")],
        [
            State("rt-fig2-modal", "is_open"),
            # State("rt-tab2-fig1", "figure"),
            State(f"{ID_PREFIX}filter-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def toggle_rt_tab2_modal(expand_clicks, is_open, filter_data):
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
        # Re-filter data to get the fresh dataframe for the modal
        from_year = filter_data.get("from_year") if filter_data else None
        to_year = filter_data.get("to_year") if filter_data else None
        companies = filter_data.get("companies") if filter_data else None

        filtered_df = filter_data_by_year_range(df, from_year, to_year)
        filtered_df = filter_data_by_companies(filtered_df, companies)

        # Generate specific figure for expanded view with LEGEND and X-AXIS
        expanded_fig = create_energy_reporting_heatmap(
            filtered_df, header_only=False, is_expanded=True
        )

        num_rows = len(filtered_df["company_name"].unique())
        calc_height = (num_rows * 25) + 120  # Added buffer for legend

        modal_graph_style = {
            "height": f"min({calc_height}px, 85vh)",
            "width": "100%",
            "margin": "20px auto",
        }

        return not is_open, modal_title, expanded_fig, modal_graph_style

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
