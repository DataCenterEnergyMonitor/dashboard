from dash import html
import dash_bootstrap_components as dbc
from components.filters.company_profile.cp_filters import create_cp_sidebar_filters


def create_cp_tab4(companies, default_company=None):
    """
    <TO DO>
    Create Tab 4 content: Company Overview.
    Shows a table (AG-Grid) with company details.
    """
    content = html.Div(
        [
            # Left sidebar with company filter
            create_cp_sidebar_filters(companies, default_company),
            # Main content area (to the right of the sidebar)
            html.Div(
                [
                    dbc.Container(
                        [
                            html.Div(
                                [
                                    html.H5(
                                        "Company Overview",
                                        className="text-left",
                                        style={"padding": "0px 15px", "marginBottom": "0px"},
                                    ),
                                    html.P(
                                        "Coming soon.",
                                        style={
                                            "fontFamily": "Inter",
                                            "fontSize": "16px",
                                            "color": "#6c757d",
                                            "padding-left": "20px",
                                            "padding-top": "30px",
                                        },
                                    ),
                                    html.Div(
                                        id="cp-company-overview-container",
                                        style={"width": "100%"},
                                    ),
                                ],
                                style={"width": "100%","margin": "35px 0"}, 
                            ),
                        ],
                        fluid=True,
                    ),
                ],
                style={
                    "marginLeft": "320px",  # sidebar width (300px) + padding (20px)
                    "marginTop": "0px",
                    "padding": "0px",
                    "minHeight": "calc(100vh - 90px)",
                    "backgroundColor": "white",
                },
            ),
        ]
    )

    return content
