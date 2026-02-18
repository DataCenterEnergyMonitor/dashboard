from dash import dcc, html
from components.filters.year_range_filter import create_year_range_component


def create_rt_filters(df):
    # Extract years from data - convert to Python int to avoid numpy serialization issues
    years = sorted([int(y) for y in df["reported_data_year"].unique()])
    min_year, max_year = int(min(years)), int(max(years))

    return html.Div(
        [
            # Sidebar container
            html.Div(
                [
                    # Header
                    html.Div(
                        [
                            html.Span([html.I(className="fas fa-filter me-2"), ""]),
                        ],
                        style={"marginBottom": "20px", "fontWeight": "bold"},
                    ),
                    html.Div(
                        [
                            create_year_range_component(
                                base_id="reporting",
                                years=years,
                                default_from=min_year,
                                default_to=max_year,
                            ),
                        ],
                        style={"marginBottom": "30px"},
                    ),
                ],
                style={
                    "width": "300px",
                    "height": "calc(100vh - 100px)",
                    "position": "fixed",
                    "left": "0",
                    "top": "100px",
                    "borderRight": "1px solid #dee2e6",
                    "padding": "20px",
                    "zIndex": "999",
                },
            ),
        ],
    )
