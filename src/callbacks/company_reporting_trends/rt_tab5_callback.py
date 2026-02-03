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


def filter_data_by_reporting_status(df, pw_status, status_col="reports_wue"):
    """Filter dataframe by reporting status values"""
    if df.empty or not pw_status:
        return df
    return df[df[status_col].isin(pw_status)]


# ID prefix for this page's components
ID_PREFIX = "rt-"


def register_rt_tab5_callbacks(app, reporting_df, pue_wue_companies_df):
    """Register callbacks for RT Tab 5 (WUE Reporting heatmap with dual-chart pattern).

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
            Output("rt-fig5-header-container", "children"),
            Output("rt-fig5-body-container", "children"),
        ],
        [
            Input(f"{ID_PREFIX}filter-store", "data"),
            Input(f"{ID_PREFIX}active-tab-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def update_rt_tab5_chart(filter_data, active_tab):
        """Update the WUE reporting heatmap based on filter selections from store"""
        # Only process if we're on tab-5 (allow None for initial load)
        if active_tab is not None and active_tab != "tab-5":
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

        # Filter by year range and company (no status filter yet)
        df_year_company = filter_data_by_year_range(
            pue_wue_companies_df, from_year, to_year, year_col="year"
        )
        df_year_company = filter_data_by_companies(df_year_company, companies)

        # Apply status filter only to determine which companies to show:
        # keep companies that have at least one row with a selected status in the range
        filtered_by_status = filter_data_by_reporting_status(
            df_year_company, pw_status, status_col="reports_wue"
        )
        visible_companies = (
            sorted(filtered_by_status["company_name"].unique())
            if not filtered_by_status.empty
            else []
        )

        # Chart data: same year+company scope, restricted to visible companies,
        # but do NOT filter by status so each cell shows the actual status
        df_for_chart = (
            df_year_company[df_year_company["company_name"].isin(visible_companies)]
            if visible_companies
            else df_year_company.iloc[0:0]
        )

        filters_applied = bool(companies) or bool(pw_status)

        # Header (legend + x-axis), sticky
        wue_trends_header_fig = create_pue_wue_reporting_heatmap_plot(
            filtered_df=df_for_chart,
            filters_applied=filters_applied,
            header_only=True,
            reporting_column="reports_wue",
        )

        # Body (scrollable data rows), fixed row height
        wue_trends_fig = create_pue_wue_reporting_heatmap_plot(
            filtered_df=df_for_chart,
            filters_applied=filters_applied,
            header_only=False,
            reporting_column="reports_wue",
        )

        num_companies = len(visible_companies)
        FIXED_ROW_HEIGHT = 25
        body_height_px = num_companies * FIXED_ROW_HEIGHT + 40

        header_card = dcc.Graph(
            figure=wue_trends_header_fig,
            config=chart_config,
            style={"height": "120px", "width": "100%"},
        )
        body_card = dcc.Graph(
            figure=wue_trends_fig,
            config=chart_config,
            style={"height": f"{body_height_px}px", "width": "100%"},
        )

        return header_card, body_card

    # Modal expand callback: build expanded figure from filter store with fixed row height
    @app.callback(
        [
            Output("rt-fig5-modal", "is_open"),
            Output("rt-fig5-modal-title", "children"),
            Output("rt-fig5-expanded", "figure"),
            Output("rt-fig5-expanded", "style"),
        ],
        [Input("expand-rt-tab5-fig1", "n_clicks")],
        [
            State("rt-fig5-modal", "is_open"),
            State(f"{ID_PREFIX}filter-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def toggle_rt_tab5_modal(expand_clicks, is_open, filter_data):
        """Toggle the expanded modal view; expanded figure uses fixed row height (no stretch)."""
        if not expand_clicks:
            raise dash.exceptions.PreventUpdate

        last_modified_date = get_rt_last_modified_date()
        if last_modified_date:
            modal_title = html.Div(
                [
                    html.Div("WUE Reporting by Company Over Time"),
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
            modal_title = "WUE Reporting by Company Over Time"

        from_year = filter_data.get("from_year") if filter_data else None
        to_year = filter_data.get("to_year") if filter_data else None
        companies = filter_data.get("companies") if filter_data else None
        pw_status = filter_data.get("pw_status") if filter_data else None

        df_year_company = filter_data_by_year_range(
            pue_wue_companies_df, from_year, to_year, year_col="year"
        )
        df_year_company = filter_data_by_companies(df_year_company, companies)
        filtered_by_status = filter_data_by_reporting_status(
            df_year_company, pw_status, status_col="reports_wue"
        )
        visible_companies = (
            sorted(filtered_by_status["company_name"].unique())
            if not filtered_by_status.empty
            else []
        )
        df_for_chart = (
            df_year_company[df_year_company["company_name"].isin(visible_companies)]
            if visible_companies
            else df_year_company.iloc[0:0]
        )
        filters_applied = bool(companies) or bool(pw_status)

        expanded_fig = create_pue_wue_reporting_heatmap_plot(
            filtered_df=df_for_chart,
            filters_applied=filters_applied,
            header_only=False,
            is_expanded=True,
            reporting_column="reports_wue",
        )

        num_rows = len(visible_companies)
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
        Output("download-rt-tab5-fig1", "data"),
        Input("download-btn-rt-tab5-fig1", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_rt_tab5_data(n_clicks):
        """Download the WUE companies data as Excel"""
        root_dir = Path(__file__).parent.parent.parent
        input_path = root_dir / "data" / "Companies_list.xlsx"

        return create_filtered_excel_download(
            input_path=input_path,
            output_filename="wue_reporting_companies.xlsx",
            sheets_to_export=["summary", "reporting_status"],
            internal_prefix="_internal_",
            n_clicks=n_clicks,
        )
