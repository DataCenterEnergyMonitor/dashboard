from dash import dcc, html
import dash_bootstrap_components as dbc

ID_PREFIX = "cp-"


def create_cp_tab3_filters(df, default_company=None):
    """
    Create the left sidebar filter panel for Company Profile Tab 3.

    Filters: company (highlight), companies to compare, reporting year.
    Apply Filters / Clear All buttons follow the same pattern as the
    Company Reporting Trends page.

    Args:
        df: energy-use dataframe that contains filter option values
        default_company: company to pre-select (propagated from filter store)

    Returns:
        html.Div wrapping the fixed sidebar
    """
    companies_list = sorted(df["company_name"].unique())
    if default_company is None:
        default_company = companies_list[0] if companies_list else None
    years = sorted(df["reported_data_year"].unique(), reverse=True)
    default_year = int(max(df["reported_data_year"])) - 1 #set previous year as a default to account for the delay in data reporting

    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(
                                [html.I(className="fas fa-filter me-2"), ""]
                            ),
                        ],
                        style={"flexShrink": "0"},
                    ),
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
                                        "Company:",
                                        className="filter-label",
                                    ),
                                    dcc.Dropdown(
                                        id=f"{ID_PREFIX}company-dropdown",
                                        options=[
                                            {"label": c, "value": c}
                                            for c in companies_list
                                        ],
                                        placeholder="Select a company",
                                        value=default_company,
                                        clearable=False,
                                        style={
                                            "fontFamily": "Inter",
                                            "fontSize": "14px",
                                        },
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box mb-3",
                                    ),
                                ],
                                className="filter-box mb-3",
                            ),
                            html.Div(
                                [
                                    html.Label(
                                        "Companies to compare:",
                                        className="filter-label",
                                    ),
                                    dcc.Dropdown(
                                        id=f"{ID_PREFIX}benchmark-companies-dropdown",
                                        options=[
                                            {"label": c, "value": c}
                                            for c in companies_list
                                        ],
                                        placeholder="All companies",
                                        multi=True,
                                        style={
                                            "fontFamily": "Inter",
                                            "fontSize": "14px",
                                        },
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box mb-3",
                                    ),
                                ],
                                className="filter-box mb-3",
                            ),
                            html.Div(
                                [
                                    html.Label(
                                        "Reporting Year:",
                                        className="filter-label",
                                    ),
                                    dcc.Dropdown(
                                        id=f"{ID_PREFIX}year-dropdown",
                                        options=[
                                            {"label": y, "value": y}
                                            for y in years
                                        ],
                                        placeholder="Select a reporting year",
                                        value=default_year,
                                        clearable=False,
                                        style={
                                            "fontFamily": "Inter",
                                            "fontSize": "14px",
                                        },
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box mb-3",
                                    ),
                                ],
                                className="filter-box mb-3",
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
                    html.Div(
                        [
                            dbc.ButtonGroup(
                                [
                                    dbc.Button(
                                        "Apply Filters",
                                        id=f"{ID_PREFIX}apply-filters-btn",
                                        color="primary",
                                        size="sm",
                                        n_clicks=0,
                                        className="mb-2",
                                        style={
                                            "width": "100%",
                                            "borderRadius": "5px",
                                        },
                                    ),
                                    dbc.Button(
                                        "Clear All",
                                        id=f"{ID_PREFIX}clear-filters-btn",
                                        color="outline-secondary",
                                        size="sm",
                                        n_clicks=0,
                                        style={
                                            "width": "100%",
                                            "borderRadius": "5px",
                                        },
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
