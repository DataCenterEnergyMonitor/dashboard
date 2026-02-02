import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc
from components.year_range import create_year_range_component


def create_rt_tab4_filters(df):
    # extract years from data - convert to Python int to avoid numpy serialization issues
    years = sorted([int(y) for y in df["year"].unique()])
    min_year, max_year = int(min(years)), int(max(years))
    reporting_status = [
        "company not established",
        "company Inactive",
        "no reporting evident",
        "individual data center values only",
        "fleet-wide values only",
        "both fleet-wide and individual data center values",
        "pending",
    ]
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
                        style={"flexShrink": "0"},
                    ),
                    # Scrollable filter content (takes remaining space)
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H5(
                                        "",
                                        className="filter-section-title",
                                        style={
                                            "color": "#34495e",
                                            "fontSize": "1.1rem",
                                            "fontWeight": "600",
                                            "marginBottom": "15px",
                                            "marginTop": "20px",
                                        },
                                    ),
                                ],
                            ),
                            html.Div(
                                [
                                    html.Label(
                                        "Reporting Year Range:",
                                        className="filter-label",
                                    ),
                                    create_year_range_component(
                                        base_id="rt",
                                        years=years,
                                        default_from=min_year,
                                        default_to=max_year,
                                    ),
                                ],
                                className="filter-box mb-3",
                            ),
                            html.Div(
                                [
                                    html.Label(
                                        "Company/Organization Name:",
                                        className="filter-label",
                                    ),
                                    dcc.Dropdown(
                                        id="rt-company-filter",
                                        options=sorted(df["company_name"].unique()),
                                        multi=True,
                                        persistence=True,
                                        persistence_type="session",
                                        placeholder="Select companies",
                                        className="filter-box mb-3",
                                    ),
                                ]
                            ),
                            html.Div(
                                [
                                    html.Label(
                                        "Reporting Status:", className="filter-label"
                                    ),
                                    dcc.Checklist(
                                        id="pw_reporting_status",
                                        options=[
                                            {
                                                "label": "Not established",
                                                "value": "company not established",
                                            },
                                            {
                                                "label": "Company inactive",
                                                "value": "company Inactive",
                                            },
                                            {
                                                "label": "No reporting",
                                                "value": "no reporting evident",
                                            },
                                            {
                                                "label": "Individual Data Centers only",
                                                "value": "individual data center values only",
                                            },
                                            {
                                                "label": "Fleet-wide only",
                                                "value": "fleet-wide values only",
                                            },
                                            {
                                                "label": "Fleet and Individual Data Centers",
                                                "value": "both fleet-wide and individual data center values",
                                            },
                                            {
                                                "label": "Pending data submission",
                                                "value": "pending",
                                            },
                                        ],
                                        value=reporting_status,
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box",
                                    ),
                                ]
                            ),
                        ],
                        style={
                            "flex": "1",
                            "minHeight": "0",
                            "overflowY": "auto",
                            "paddingRight": "10px",
                            "paddingBottom": "50px",
                            "position": "relative",
                            "zIndex": "10",
                        },
                    ),
                    # Buttons pinned at end of sidebar
                    html.Div(
                        [
                            dbc.ButtonGroup(
                                [
                                    dbc.Button(
                                        "Apply Filters",
                                        id="apply-filters-btn",
                                        color="primary",
                                        size="sm",
                                        n_clicks=0,
                                        className="mb-2",
                                        style={"width": "100%", "borderRadius": "5px"},
                                    ),
                                    dbc.Button(
                                        "Clear All",
                                        id="rt-clear-filters-btn",
                                        color="outline-secondary",
                                        size="sm",
                                        n_clicks=0,
                                        style={"width": "100%", "borderRadius": "5px"},
                                    ),
                                ],
                                vertical=True,
                                className="w-100",
                            )
                        ],
                        style={
                            "position": "sticky",
                            "bottom": "0",
                            "flexShrink": "0",
                            "backgroundColor": "#f8f9fa",
                            "padding": "15px 0",
                            "marginTop": "20px",
                            "borderTop": "1px solid #dee2e6",
                        },
                    ),
                    # Hidden div to store applied filter state
                    html.Div(id="applied-filters-store", style={"display": "none"}),
                ],
                style={
                    "width": "300px",
                    "height": "calc(100vh - 100px)",
                    "position": "fixed",
                    "left": "0",
                    "top": "100px",
                    "borderRight": "1px solid #dee2e6",
                    "padding": "20px",
                    "paddingTop": "20px",
                    "paddingBottom": "5px",
                    "paddingLeft": "20px",
                    "paddingRight": "20px",
                    "zIndex": "999",
                    "display": "flex",
                    "flexDirection": "column",
                },
            )
        ]
    )


# def get_options(column, filtered_df):
#     """Get unique options from filtered dataframe"""
#     return [{'label': val, 'value': val} for val in sorted(filtered_df[column].unique())]
