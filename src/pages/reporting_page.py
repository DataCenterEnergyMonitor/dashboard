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
                duration=4000,  # Auto-dismiss after 4 seconds
                style={
                    "position": "fixed",
                    "top": 20,
                    "right": 20,
                    "zIndex": 999,
                    "width": "300px",
                    "backgroundColor": "#f8d7da",  # Light red background
                    "color": "#721c24",  # Dark red text
                },
            ),
            # Left side - Filter Panel
            html.Div(
                [
                    # Filter icon header - left aligned
                    html.Div(
                        html.I(
                            className="fas fa-filter",
                            style={
                                "fontSize": "24px",
                                "color": "#4CAF50",
                                "marginBottom": "20px",
                            },
                        ),
                        style={
                            "display": "flex",
                            "justifyContent": "flex-start",  # Left aligned
                            "width": "100%",
                        },
                    ),
                    year_range_filter,
                ],
                style={
                    "width": "260px",
                    "padding": "20px",
                    "backgroundColor": "#f8f9fa",
                    "borderRight": "1px solid #dee2e6",
                },
            ),
            # Right side - Charts
            html.Div(
                [
                    html.H1(
                        "Trends in Data Center Energy Reporting Over Time",
                        className="page-title",
                    ),
                    html.Div(
                        [
                            # Download button above charts
                            create_download_button(
                                button_id="btn-download-reporting-data",
                                download_id="download-reporting-data",
                            ),
                            # Bar Chart
                            dcc.Graph(
                                id="reporting-bar-chart",
                                style={"height": "500px", "marginBottom": "20px"},
                            ),
                            # Timeline Chart
                            dcc.Graph(
                                id="timeline-bar-chart", style={"height": "600px"}
                            ),
                        ],
                        style={"width": "90%", "margin": "0 auto"},
                    ),
                ],
                style={"flex": "1", "padding": "20px", "backgroundColor": "#ffffff"},
            ),
        ],
        style={"display": "flex", "minHeight": "100vh", "backgroundColor": "#ffffff"},
    )

    return create_base_layout(content)
