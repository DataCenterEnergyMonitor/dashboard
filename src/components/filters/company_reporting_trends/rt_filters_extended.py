from dash import dcc, html
import dash_bootstrap_components as dbc
from components.year_range import create_year_range_component


def create_rt_filters_extended(reporting_df, companies_df):
    """
    Create extended filters for tabs 2-5.
    Includes year range filter (shared with tab 1) and company filter.

    Args:
        reporting_df: DataFrame with reporting data (for year range)
        companies_df: DataFrame with companies list (for company filter)
    """
    # Extract years from data - convert to Python int to avoid numpy serialization issues
    years = sorted([int(y) for y in reporting_df["reported_data_year"].unique()])
    min_year, max_year = int(min(years)), int(max(years))

    # Extract companies from companies_df
    companies = sorted(companies_df["company_name"].unique().tolist())
    company_options = [{"label": c, "value": c} for c in companies]

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
                    # Year range filter (shared with tab 1)
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
                    # Company filter (tabs 2-5 only)
                    html.Div(
                        [
                            html.Label(
                                "Company",
                                style={
                                    "fontWeight": "500",
                                    "marginBottom": "8px",
                                    "display": "block",
                                },
                            ),
                            dcc.Dropdown(
                                id="rt-company-filter",
                                options=company_options,
                                value=None,
                                multi=True,
                                placeholder="Select companies...",
                                style={"width": "100%"},
                                className="filter-dropdown",
                            ),
                        ],
                        style={"marginBottom": "20px"},
                    ),
                    # Clear filters button
                    html.Div(
                        [
                            dbc.Button(
                                [
                                    html.I(className="fas fa-times me-2"),
                                    "Clear Filters",
                                ],
                                id="rt-clear-filters-btn",
                                color="secondary",
                                outline=True,
                                size="sm",
                                style={"width": "100%"},
                            ),
                        ],
                        style={"marginTop": "20px"},
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
                    "overflowY": "auto",
                },
            ),
        ],
    )
