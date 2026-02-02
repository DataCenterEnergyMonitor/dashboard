import dash
from pathlib import Path
from dash import Input, Output, State, dcc, html
import json
from datetime import datetime
from charts.pue_wue_reporting_heatmap import create_pue_wue_reporting_heatmap_plot
from components.excel_export import create_filtered_excel_download


def get_rt_last_modified_date():
    """Get the last modified date for reporting data from metadata.json"""
    try:
        root_dir = Path(__file__).parent.parent.parent.parent
        json_path = root_dir / "data" / "dependencies" / "metadata.json"

        if not json_path.exists():
            return None

        with open(json_path, "r") as f:
            metadata = json.load(f)

        for file_info in metadata.get("files", []):
            if "companies" in file_info.get("source_file", "").lower():
                last_modified = file_info.get("last_modified")
                if last_modified:
                    dt = datetime.fromisoformat(last_modified)
                    return dt.strftime("%B %d, %Y")

        return None
    except (FileNotFoundError, KeyError, ValueError) as e:
        print(f"Warning: Could not load last modified date: {e}")
        return None


def filter_data_by_year_range(df, from_year, to_year, year_col="year"):
    """Filter dataframe by year range"""
    if df.empty:
        return df

    filtered_df = df.copy()

    if from_year is not None:
        filtered_df = filtered_df[filtered_df[year_col] >= from_year]

    if to_year is not None:
        filtered_df = filtered_df[filtered_df[year_col] <= to_year]

    return filtered_df


def filter_data_by_companies(df, companies, company_col="company_name"):
    """Filter dataframe by selected companies"""
    if df.empty or not companies:
        return df
    return df[df[company_col].isin(companies)]


def filter_data_by_reporting_status(df, pw_status, status_col="reports_pue"):
    """Filter dataframe by reporting status values"""
    if df.empty or not pw_status:
        return df
    return df[df[status_col].isin(pw_status)]


# ID prefix for this page's components
ID_PREFIX = "rt-"


def register_rt_tab4_callbacks(app, pue_wue_companies_df):
    """Register callbacks for RT Tab 4 (PUE Reporting heatmap with dual-chart pattern).

    Uses header + scrollable main chart like pue_wue_page.
    Filters are inside each tab. Filter values are synced via rt-filter-store.
    """

    # Chart config for the graphs
    chart_config = {
        "responsive": True,
        "displayModeBar": False,
        "displaylogo": False,
    }

    # Callback to update chart when filters or tab changes
    @app.callback(
        [
            Output("rt-fig4-header-container", "children"),
            Output("rt-fig4-body-container", "children"),
        ],
        [
            Input(f"{ID_PREFIX}filter-store", "data"),
            Input(f"{ID_PREFIX}active-tab-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def update_rt_tab4_chart(filter_data, active_tab):
        """Update the PUE reporting heatmap based on filter selections from store"""
        # Only process if we're on tab-4 (allow None for initial load)
        if active_tab is not None and active_tab != "tab-4":
            raise dash.exceptions.PreventUpdate

        # Get filter values from store
        from_year = None
        to_year = None
        companies = None
        pw_status = None

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
            pw_status = filter_data.get("pw_status")

        # Filter pue_wue_companies_df by year range (uses "year" column)
        filtered_df = filter_data_by_year_range(
            pue_wue_companies_df, from_year, to_year, year_col="year"
        )

        # Filter by companies if selected
        filtered_df = filter_data_by_companies(filtered_df, companies)

        # Filter by reporting status if selected
        filtered_df = filter_data_by_reporting_status(
            filtered_df, pw_status, status_col="reports_pue"
        )

        # Determine if filters are applied
        filters_applied = bool(companies) or bool(pw_status)

        # Header (legend + x-axis), sticky
        pue_trends_header_fig = create_pue_wue_reporting_heatmap_plot(
            filtered_df=filtered_df,
            filters_applied=filters_applied,
            header_only=True,
            reporting_column="reports_pue",
        )

        # Body (scrollable data rows), fixed row height
        pue_trends_fig = create_pue_wue_reporting_heatmap_plot(
            filtered_df=filtered_df,
            filters_applied=filters_applied,
            header_only=False,
            reporting_column="reports_pue",
        )

        num_companies = len(filtered_df["company_name"].unique()) if not filtered_df.empty else 0
        FIXED_ROW_HEIGHT = 25
        body_height_px = num_companies * FIXED_ROW_HEIGHT + 40

        header_card = dcc.Graph(
            figure=pue_trends_header_fig,
            config=chart_config,
            style={"height": "120px", "width": "100%"},
        )
        body_card = dcc.Graph(
            figure=pue_trends_fig,
            config=chart_config,
            style={"height": f"{body_height_px}px", "width": "100%"},
        )

        return header_card, body_card

    # Modal expand callback: build expanded figure from filter store with fixed row height
    @app.callback(
        [
            Output("rt-fig4-modal", "is_open"),
            Output("rt-fig4-modal-title", "children"),
            Output("rt-fig4-expanded", "figure"),
            Output("rt-fig4-expanded", "style"),
        ],
        [Input("expand-rt-tab4-fig1", "n_clicks")],
        [
            State("rt-fig4-modal", "is_open"),
            State(f"{ID_PREFIX}filter-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def toggle_rt_tab4_modal(expand_clicks, is_open, filter_data):
        """Toggle the expanded modal view; expanded figure uses fixed row height (no stretch)."""
        if not expand_clicks:
            raise dash.exceptions.PreventUpdate

        last_modified_date = get_rt_last_modified_date()
        if last_modified_date:
            modal_title = html.Div(
                [
                    html.Div("PUE Reporting by Company Over Time"),
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
            modal_title = "PUE Reporting by Company Over Time"

        from_year = filter_data.get("from_year") if filter_data else None
        to_year = filter_data.get("to_year") if filter_data else None
        companies = filter_data.get("companies") if filter_data else None
        pw_status = filter_data.get("pw_status") if filter_data else None

        filtered_df = filter_data_by_year_range(
            pue_wue_companies_df, from_year, to_year, year_col="year"
        )
        filtered_df = filter_data_by_companies(filtered_df, companies)
        filtered_df = filter_data_by_reporting_status(
            filtered_df, pw_status, status_col="reports_pue"
        )
        filters_applied = bool(companies) or bool(pw_status)

        expanded_fig = create_pue_wue_reporting_heatmap_plot(
            filtered_df=filtered_df,
            filters_applied=filters_applied,
            header_only=False,
            is_expanded=True,
            reporting_column="reports_pue",
        )

        num_rows = (
            len(filtered_df["company_name"].unique()) if not filtered_df.empty else 0
        )
        FIXED_ROW_HEIGHT = 25
        calc_height = num_rows * FIXED_ROW_HEIGHT + 120
        modal_graph_style = {
            "height": f"min({calc_height}px, 85vh)",
            "width": "100%",
            "margin": "20px auto",
        }

        return not is_open, modal_title, expanded_fig, modal_graph_style

    # Download data callback
    @app.callback(
        Output("download-rt-tab4-fig1", "data"),
        Input("download-btn-rt-tab4-fig1", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_rt_tab4_data(n_clicks):
        """Download the PUE companies data as Excel"""
        root_dir = Path(__file__).parent.parent.parent
        input_path = root_dir / "data" / "Companies_list.xlsx"

        return create_filtered_excel_download(
            input_path=input_path,
            output_filename="pue_reporting_companies.xlsx",
            sheets_to_export=["summary", "reporting_status"],
            internal_prefix="_internal_",
            n_clicks=n_clicks,
        )

    # Callback to handle Clear All button - resets filter UI components
    # The store is updated separately in rt_tab1_callback.py
    @app.callback(
        [
            Output("rt-from-year", "value", allow_duplicate=True),
            Output("rt-to-year", "value", allow_duplicate=True),
            Output("rt-company-filter", "value", allow_duplicate=True),
            Output("pw_reporting_status", "value", allow_duplicate=True),
        ],
        [Input("rt-clear-filters-btn", "n_clicks")],
        prevent_initial_call=True,
    )
    def clear_all_filters(clear_clicks):
        if clear_clicks:
            # Clear all filter values - reset pw_status to default (all selected)
            default_pw_status = [
                "company not established",
                "company Inactive",
                "no reporting evident",
                "individual data center values only",
                "fleet-wide values only",
                "both fleet-wide and individual data center values",
                "pending",
            ]
            return (
                None,
                None,
                None,
                default_pw_status,
            )
        return dash.no_update
