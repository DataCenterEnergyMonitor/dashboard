from dash import dcc, html
import dash_bootstrap_components as dbc
from components.filters.reporting_trends.rt_tab5_filters import (
    create_rt_tab5_filters,
)
from callbacks.reporting_trends.rt_tab5_callback import (
    get_rt_last_modified_date,
)


def create_rt_tab5(app, df=None):
    """
    Create tab 5 content (WUE Reporting heatmap with dual-chart pattern).
    Uses header + scrollable main chart like tab 2.
    Filters are inside the tab and sync via rt-filter-store.
    Includes company filter (shared with tabs 2-5).
    """
    last_modified_date = get_rt_last_modified_date()
    content = html.Div(
        [
            # Sticky sidebar wrapper with extended filters (year + company)
            create_rt_tab5_filters(df),
            html.Div(
                [
                    # Mobile navigation
                    html.Div(
                        [
                            dbc.Nav(
                                [
                                    dbc.NavLink(
                                        "WUE Reporting by Company Over Time",
                                        href="#rt-tab5-nav",
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
                            # Static title and action buttons (remain fixed when callback runs)
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                "WUE Reporting by Company Over Time",
                                                style={
                                                    "fontSize": "1.25rem",
                                                    "fontWeight": "500",
                                                },
                                            ),
                                            (
                                                html.Div(
                                                    f"(as of {last_modified_date})",
                                                    style={
                                                        "fontSize": "0.85em",
                                                        "color": "#666",
                                                        "marginTop": "4px",
                                                    },
                                                )
                                                if last_modified_date
                                                else None
                                            ),
                                        ],
                                        className="text-left",
                                    ),
                                    html.Div(
                                        [
                                            dbc.Button(
                                                [
                                                    html.I(
                                                        className="fas fa-download",
                                                        style={"marginRight": "6px"},
                                                    ),
                                                    html.Span(
                                                        "Data .xlsx",
                                                        style={"fontSize": "0.8rem"},
                                                    ),
                                                ],
                                                id="download-btn-rt-tab5-fig1",
                                                size="sm",
                                                color="light",
                                                className="me-2",
                                                title="Download figure data",
                                            ),
                                            dbc.Tooltip(
                                                "Download figure data as Excel file",
                                                target="download-btn-rt-tab5-fig1",
                                                placement="bottom",
                                            ),
                                            dbc.Button(
                                                [
                                                    html.I(
                                                        className="fas fa-expand",
                                                        style={"marginRight": "6px"},
                                                    ),
                                                    html.Span(
                                                        "Expand",
                                                        style={"fontSize": "0.8rem"},
                                                    ),
                                                ],
                                                id="expand-rt-tab5-fig1",
                                                size="sm",
                                                color="light",
                                                title="Expand figure",
                                            ),
                                            dbc.Tooltip(
                                                "View figure in expanded window",
                                                target="expand-rt-tab5-fig1",
                                                placement="bottom",
                                            ),
                                        ],
                                        className="float-end",
                                    ),
                                    dcc.Download(id="download-rt-tab5-fig1"),
                                ],
                                style={
                                    "border": "none",
                                    "padding": "25px 15px",
                                    "marginBottom": "0px",
                                    "backgroundColor": "#ffffff",
                                },
                            ),
                            # Figure: header (sticky) + body (scrollable), updated by callback
                            dcc.Loading(
                                id="rt-fig5-loading",
                                type="circle",
                                color="#395970",
                                children=html.Div(
                                    [
                                        html.Div(
                                            id="rt-fig5-header-container",
                                            style={
                                                "position": "sticky",
                                                "top": "0",
                                                "zIndex": "999",
                                                "backgroundColor": "white",
                                            },
                                        ),
                                        html.Div(
                                            id="rt-fig5-body-container",
                                            style={
                                                "maxHeight": "600px",
                                                "overflowY": "auto",
                                                "overflowX": "hidden",
                                            },
                                        ),
                                    ],
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
                        # style={"marginTop": "35px"},
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
                    dbc.ModalHeader(dbc.ModalTitle(id="rt-fig5-modal-title")),
                    dbc.ModalBody(
                        [
                            dcc.Graph(
                                id="rt-fig5-expanded",
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
                id="rt-fig5-modal",
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
