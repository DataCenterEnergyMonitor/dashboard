from dash import dcc, html
import dash_bootstrap_components as dbc
from components.filters.company_reporting_trends.rt_filters import create_rt_filters


def create_rt_tab1(app, reporting_df):
    """
    Create tab 1 content (Reporting Adoption barchart).
    Filters are inside the tab and sync via rt-filter-store.
    """
    content = html.Div(
        [
            # Sticky sidebar wrapper with filters
            create_rt_filters(reporting_df),
            html.Div(
                [
                    # Mobile navigation
                    html.Div(
                        [
                            dbc.Nav(
                                [
                                    dbc.NavLink(
                                        "Data Center Reporting Over Time",
                                        href="#rt-tab1-nav",
                                        className="px-2",
                                    ),
                                ],
                                horizontal=True,
                                pills=True,
                                className="justify-content-center",
                            )
                        ],
                        className="d-block d-lg-none",  # show on <992px, hide on ≥992px
                        style={
                            "position": "fixed",
                            "top": "80px",
                            "left": "0",
                            "right": "0",
                            "zIndex": "1000",
                            "backgroundColor": "white",
                            "padding": "8px 10px",
                            "height": "60px",
                            "borderBottom": "1px solid #dee2e6",
                            "overflow": "hidden",
                        },
                    ),
                    dbc.Container(
                        [
                            # Figure container (updated by callback)
                            html.Div(id="rt-fig1-container"),
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
            # Modal for expanded view
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle(id="rt-tab1-fig1-modal-title")),
                    dbc.ModalBody(
                        [
                            dcc.Graph(
                                id="rt-tab1-expanded-fig1",
                                style={
                                    "height": "calc(100vh - 56px)",  # 56px = header height
                                    "width": "100vw",
                                    "margin": "0",
                                    "padding": "0",
                                },
                            )
                        ],
                        style={"padding": "0", "margin": "0"},
                    ),
                ],
                id="rt-fig1-modal",
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
