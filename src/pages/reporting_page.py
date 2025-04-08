from dash import html, dcc
import dash_bootstrap_components as dbc
from components.year_range import create_year_range_component
from components.download_button import create_download_button
from layouts.base_layout import create_base_layout
# from callbacks.reporting_callbacks import create_reporting_callback


def create_reporting_page(app, reporting_df, data_dict, chart_configs):
    """Create the reporting page with year range filter"""
    years = sorted(reporting_df["reported_data_year"].unique())
    min_year, max_year = min(years), max(years)

    # Create year range filter using the component
    year_range_filter = create_year_range_component(
        base_id="reporting", years=years, default_from=min_year, default_to=max_year
    )

    content = html.Div(
        [
            # Error notification toast
            dbc.Toast(
                id="reporting-error-toast",
                is_open=False,
                dismissable=True,
                duration=4000,
                style={
                    "position": "fixed",
                    "top": 20,
                    "right": 20,
                    "zIndex": 999,
                    "width": "300px",
                },
                className="bg-danger text-white",
            ),
            # Main content area
            dbc.Col(
                [
                    # Header section
                    html.H1(
                        "Trends in Data Center Energy Reporting Over Time",
                        className="page-title h2 mb-3",
                    ),
                    dbc.Container(
                        [
                            # Filter and Download button row
                            dbc.Row(
                                [
                                    # Left offset to align with chart
                                    dbc.Col(lg=1),
                                    # Date range filter
                                    dbc.Col(
                                        [
                                            # html.Label(
                                            #     "Select Date Range",
                                            #     className="text-muted mb-2",
                                            # ),
                                            year_range_filter,
                                        ],
                                        width=12,
                                        lg=4,
                                    ),
                                    # Spacer that takes remaining space
                                    dbc.Col(className="flex-grow-1"),
                                    # Download button (right-aligned)
                                    dbc.Col(
                                        create_download_button(
                                            button_id="btn-download-reporting-data",
                                            download_id="download-reporting-data",
                                        ),
                                        width="auto",
                                    ),
                                    # Right offset to match chart container
                                    dbc.Col(lg=1),
                                ],
                                className="mb-1 align-items-end",
                            ),
                            # Charts
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            # Bar Chart
                                            dbc.Card(
                                                dcc.Graph(
                                                    id="reporting-bar-chart",
                                                    className="h-100",
                                                    config={
                                                        "responsive": True,
                                                        "staticPlot": False,
                                                        "scrollZoom": False,
                                                        "doubleClick": False,
                                                        "showTips": False,
                                                    },
                                                    style={"height": "100%"},
                                                ),
                                                className="mb-4",
                                                style={
                                                    "height": "52vh",
                                                    "border": "1px solid rgba(0,0,0,.125)",
                                                    "transition": "none",
                                                    "box-shadow": "none",
                                                    "transform": "none",
                                                    "cursor": "default",
                                                    "userSelect": "none",
                                                    "-webkit-transform": "none",
                                                    "-webkit-transition": "none",
                                                },
                                            ),
                                            # Timeline Chart
                                            dbc.Card(
                                                dcc.Graph(
                                                    id="timeline-bar-chart",
                                                    config={
                                                        "responsive": True,
                                                        "staticPlot": False,
                                                        "scrollZoom": False,
                                                        "doubleClick": False,
                                                        "showTips": False,
                                                    },
                                                    style={
                                                        "height": "100%",
                                                        "minHeight": "500px",
                                                    },
                                                ),
                                                style={
                                                    "minHeight": "500px",
                                                    "border": "1px solid rgba(0,0,0,.125)",
                                                    "transition": "none",
                                                    "box-shadow": "none",
                                                    "transform": "none",
                                                    "cursor": "default",
                                                    "userSelect": "none",
                                                    "-webkit-transform": "none",
                                                    "-webkit-transition": "none",
                                                },
                                            ),
                                        ],
                                        lg={"size": 10, "offset": 1},
                                        className="px-2",
                                    ),
                                ]
                            ),
                        ],
                        fluid=True,
                        className="px-3 mt-2",
                    ),
                ],
                width=12,
                className="p-4 bg-white",
            ),
        ],
        className="min-vh-100",
    )

    return create_base_layout(content)
