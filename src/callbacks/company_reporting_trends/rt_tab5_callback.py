import dash
from pathlib import Path
from dash import Input, Output, State, dcc, html
import dash_bootstrap_components as dbc
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
        Output("rt-fig5-container", "children"),
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

        # Filter pue_wue_companies_df by year range (uses "year" column)
        filtered_df = filter_data_by_year_range(
            pue_wue_companies_df, from_year, to_year, year_col="year"
        )

        # Filter by companies if selected
        filtered_df = filter_data_by_companies(filtered_df, companies)

        # Determine if filters are applied
        filters_applied = bool(companies)

        # Create WUE Trends chart (main scrollable chart)
        wue_trends_fig = create_pue_wue_reporting_heatmap_plot(
            filtered_df=filtered_df,
            filters_applied=filters_applied,
            header_only=False,
            reporting_column="reports_wue",
        )

        # Create WUE Trends header chart (sticky header with legend and x-axis)
        wue_trends_header_fig = create_pue_wue_reporting_heatmap_plot(
            filtered_df=filtered_df,
            filters_applied=filters_applied,
            header_only=True,
            reporting_column="reports_wue",
        )

        # Get last modified date for title
        last_modified_date = get_rt_last_modified_date()
        if last_modified_date:
            title = html.Div(
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
            title = "WUE Reporting by Company Over Time"

        # Create dual-chart layout (header + scrollable main chart)
        chart_card = dbc.Card(
            [
                dbc.CardHeader(
                    [
                        html.H5(title, className="text-left"),
                        html.Div(
                            [
                                dbc.Button(
                                    [
                                        html.I(
                                            className="fas fa-download",
                                            style={"marginRight": "6px"},
                                        ),
                                        html.Span(
                                            "Data .xlsx",
                                            style={"fontSize": "0.8rem"},
                                        ),
                                    ],
                                    id="download-btn-rt-tab5-fig1",
                                    size="sm",
                                    color="light",
                                    className="me-2",
                                ),
                                dbc.Tooltip(
                                    "Download chart data as Excel file",
                                    target="download-btn-rt-tab5-fig1",
                                    placement="bottom",
                                ),
                                dbc.Button(
                                    [
                                        html.I(
                                            className="fas fa-expand",
                                            style={"marginRight": "6px"},
                                        ),
                                        html.Span(
                                            "Expand",
                                            style={"fontSize": "0.8rem"},
                                        ),
                                    ],
                                    id="expand-rt-tab5-fig1",
                                    size="sm",
                                    color="light",
                                ),
                                dbc.Tooltip(
                                    "View chart in expanded window",
                                    target="expand-rt-tab5-fig1",
                                    placement="bottom",
                                ),
                            ],
                            className="float-end",
                        ),
                        dcc.Download(id="download-rt-tab5-fig1"),
                    ],
                    style={
                        "border": "none",
                        "padding": "8px 15px",
                        "marginBottom": "0px",
                        "backgroundColor": "#ffffff",
                    },
                ),
                dbc.CardBody(
                    html.Div(
                        [
                            # Sticky header (legend + x-axis)
                            html.Div(
                                [
                                    dcc.Graph(
                                        id="rt-tab5-fig1-header",
                                        figure=wue_trends_header_fig,
                                        config=chart_config,
                                        style={
                                            "height": "100px",
                                            "width": "100%",
                                            "marginBottom": "0px",
                                        },
                                    )
                                ],
                                style={
                                    "position": "sticky",
                                    "top": "0px",
                                    "backgroundColor": "white",
                                    "zIndex": "50",
                                },
                            ),
                            # Scrollable main chart
                            html.Div(
                                [
                                    dcc.Graph(
                                        id="rt-tab5-fig1",
                                        figure=wue_trends_fig,
                                        config=chart_config,
                                        style={"height": "auto", "width": "100%"},
                                    )
                                ],
                                style={
                                    "overflowY": "auto",
                                    "overflowX": "hidden",
                                    "maxHeight": "calc(65vh - 100px)",
                                },
                            ),
                        ],
                        style={"position": "relative"},
                    ),
                    style={
                        "border": "none",
                        "paddingTop": "0px",
                        "backgroundColor": "#ffffff",
                        "height": "auto",
                    },
                ),
            ],
            style={"border": "none", "boxShadow": "none", "height": "auto"},
        )

        return html.Div(
            [
                html.A(id="rt-tab5-nav"),
                dbc.Row(
                    [
                        dbc.Col(
                            [chart_card],
                            xs=12,
                            sm=12,
                            md=12,
                            lg=12,
                            className="ps-0 pe-3",
                        ),
                    ],
                    className="mb-3 gx-2",
                ),
            ],
            style={"margin": "35px 0"},
        )

    # Modal expand callback
    @app.callback(
        [
            Output("rt-fig5-modal", "is_open"),
            Output("rt-fig5-modal-title", "children"),
            Output("rt-fig5-expanded", "figure"),
        ],
        [Input("expand-rt-tab5-fig1", "n_clicks")],
        [
            State("rt-fig5-modal", "is_open"),
            State("rt-tab5-fig1", "figure"),
        ],
        prevent_initial_call=True,
    )
    def toggle_rt_tab5_modal(expand_clicks, is_open, current_figure):
        """Toggle the expanded modal view"""
        if not expand_clicks:
            raise dash.exceptions.PreventUpdate

        last_modified_date = get_rt_last_modified_date()
        if last_modified_date:
            modal_title = html.Div(
                [
                    html.Div("WUE Reporting by Company Over Time - Expanded View"),
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
            modal_title = "WUE Reporting by Company Over Time - Expanded View"

        return (
            not is_open,
            modal_title,
            current_figure or {},
        )

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
