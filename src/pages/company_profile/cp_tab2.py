from dash import dcc, html
import dash_bootstrap_components as dbc
from components.filters.company_profile.cp_filters import create_cp_sidebar_filters


def create_cp_tab2(companies, default_company=None):
    """
    Create Tab 2 content: Energy Trends.
    Shows energy consumption over time for the selected company.
    """
    content = html.Div(
        [
            create_cp_sidebar_filters(companies, default_company),
            html.Div(
                [
                    dbc.Container(
                        [
                            dcc.Loading(
                                id="cp-tab2-loading",
                                type="circle",
                                color="#395970",
                                children=html.Div(
                                    id="cp-tab2-chart-container",
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
            # Modal for expanded view
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle(id="cp-tab2-fig1-modal-title")
                    ),
                    dbc.ModalBody(
                        [
                            dcc.Graph(
                                id="cp-tab2-expanded-fig1",
                                style={
                                    "height": "calc(100vh - 56px)",
                                    "width": "100vw",
                                    "margin": "0",
                                    "padding": "0",
                                },
                            )
                        ],
                        style={"padding": "0", "margin": "0"},
                    ),
                ],
                id="cp-tab2-fig1-modal",
                fullscreen=True,
                is_open=False,
                style={
                    "maxWidth": "100vw",
                    "width": "100vw",
                    "height": "100vh",
                    "margin": "0",
                    "padding": "0",
                    "top": "0",
                    "left": "0",
                },
            ),
        ]
    )

    return content
