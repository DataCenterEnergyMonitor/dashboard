from dash import dcc, html
import dash_bootstrap_components as dbc
from components.filters.company_reporting_trends.rt_tab4_filters import (
    create_rt_tab4_filters,
)


def create_rt_tab4(app, pue_wue_companies_df=None):
    """
    Create tab 4 content (PUE Reporting heatmap with dual-chart pattern).
    Uses header + scrollable main chart like pue_wue_page.
    Filters are inside the tab and sync via rt-filter-store.
    Includes company filter (shared with tabs 2-5).
    """
    content = html.Div(
        [
            # Sticky sidebar wrapper with extended filters (year + company)
            create_rt_tab4_filters(pue_wue_companies_df),
            html.Div(
                [
                    # Mobile navigation
                    html.Div(
                        [
                            dbc.Nav(
                                [
                                    dbc.NavLink(
                                        "PUE Reporting by Company Over Time",
                                        href="#rt-tab4-nav",
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
                            # Figure container with dual-chart layout (updated by callback)
                            # Wrapped with dcc.Loading for visual feedback during chart generation
                            dcc.Loading(
                                id="rt-fig4-loading",
                                type="circle",
                                color="#395970",
                                children=html.Div(
                                    id="rt-fig4-container",
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
                    dbc.ModalHeader(dbc.ModalTitle(id="rt-fig4-modal-title")),
                    dbc.ModalBody(
                        [
                            dcc.Graph(
                                id="rt-fig4-expanded",
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
                id="rt-fig4-modal",
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
