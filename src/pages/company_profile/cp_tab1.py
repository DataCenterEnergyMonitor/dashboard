from dash import dcc, html
import dash_bootstrap_components as dbc
from components.filters.company_profile.cp_store_filters import create_cp_sidebar_filters


def create_cp_tab1(companies, default_company=None):
    """
    Create Tab 1 content: Reporting Profile table (AG-Grid)
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
                            dcc.Loading(
                                id="cp-tab1-loading",
                                type="circle",
                                color="#395970",
                                children=html.Div(
                                    id="cp-tab1-container",
                                    style={"width": "100%"},
                                ),
                                overlay_style={
                                    "visibility": "visible",
                                    "opacity": 0.8,
                                    "backgroundColor": "white",
                                },
                                parent_style={
                                    "minHeight": "400px",
                                    "width": "100%",
                                },
                            ),
                        ],
                        fluid=True,
                    ),
                ],
                style={
                    "marginLeft": "320px",
                    "marginTop": "0px",
                    "padding": "0px",
                    "minHeight": "calc(100vh - 90px)",
                    "backgroundColor": "white",
                },
            ),
        ]
    )

    return content
