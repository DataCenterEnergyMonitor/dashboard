from dash import dcc, html
import dash_bootstrap_components as dbc

# ID prefix for company profile page components
ID_PREFIX = "cp-"


def create_cp_sidebar_filters(companies, default_company=None):
    """
    Create the left sidebar filter panel for the Company Profile page.
    Contains the shared company dropdown that persists across all tabs
    via cp-filter-store.

    Args:
        companies: sorted list of company names for the dropdown
        default_company: initially selected company (or None)

    Returns:
        html.Div wrapping the fixed sidebar
    """
    return html.Div(
        [
            # Sidebar container
            html.Div(
                [
                    # Header with filter icon
                    html.Div(
                        [
                            html.Span(
                                [html.I(className="fas fa-filter me-2"), ""]
                            ),
                        ],
                        style={"flexShrink": "0"},
                    ),
                    # Scrollable filter content
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
                                            for c in companies
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
