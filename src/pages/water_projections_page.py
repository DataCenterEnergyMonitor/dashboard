import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc
from layouts.base_layout import create_base_layout
from components.bookmark_bar import create_bookmark_bar
from components.filters.water_projections_filters import (
    create_water_projections_filters,
)


# define bookmark sections
sections = [
    # {"id": "water-projections", "title": "Energy Projections"},
    # {"id": "power-projections", "title": "Power Projections"},
]

subnav_items = [
    {"id": "pue-subnav", "title": "Methodology", "href": "/pue-methodology"},
    # {"id": "wue-subnav", "title": "WUE", "href": "/wue-methodology"},
    {"id": "wue-subnav", "title": "Dataset"},
]


def create_chart_row(
    chart_id,
    title,
    expand_id,
    accordion_children=None,
    accordion_title=None,
    filename="chart",
    figure=None,
):
    """
    Create a standardized chart row with consistent styling

    Args:
        chart_id: ID for the graph component
        title: Chart title for header
        expand_id: ID for expand button
        description_md: Markdown description for right column
        filename: Filename for image download
    """

    # Chart config
    chart_config = {
        "responsive": True,
        "displayModeBar": True,
        "modeBarButtons": [
            ["toImage"],
            ["zoomIn2d"],
            ["zoomOut2d"],
            ["pan2d"],
            ["autoScale2d"],
        ],
        "displaylogo": False,
        "toImageButtonOptions": {
            "format": "png",
            "filename": filename,
            "height": 700,
            "width": 1200,
            "scale": 1,
        },
    }

    # Page layout styles
    card_header_style = {
        "border": "none",
        "padding": "0px 15px",
        "marginBottom": "0px",
        "backgroundColor": "#ffffff",
    }
    card_body_style = {
        "border": "none",
        "paddingTop": "0px",
        "backgroundColor": "#ffffff",
        "minHeight": "65vh",
    }
    card_style = {"border": "none", "boxShadow": "none", "height": "auto"}
    graph_style = {
        "height": "65vh",
        "width": "100%",
        "marginTop": "0px",
        "paddingTop": "0px",
        "border": "none",
    }
    graph_layout = {
        "autosize": True,
        "margin": {"l": 60, "r": 120, "t": 20, "b": 60},
        "height": None,
    }
    # description_style = {"textAlign": "center", "backgroundColor": "#f8f9fa", "padding": "10px", "borderRadius": "5px", "font-size": "0.8rem"}

    # if accordion_children:
    accordion_element = html.Div(
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    children=accordion_children,
                    title=accordion_title,
                ),
            ],
            flush=True,
            start_collapsed=True,
            className="filter-accordion",
            style={"width": "80%"},
        ),
    )
    # else:
    #     accordion_element = None

    return dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                [
                                    html.H5(title, className="text-left"),
                                    accordion_element if accordion_children else None,
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
                                                id=f"download-btn-{chart_id}",
                                                size="sm",
                                                color="light",
                                                className="me-2",
                                                title="Download chart data",
                                            ),
                                            dbc.Tooltip(
                                                "Download chart data as Excel file",
                                                target=f"download-btn-{chart_id}",
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
                                                id=expand_id,
                                                size="sm",
                                                color="light",
                                                title="Expand chart",
                                            ),
                                            dbc.Tooltip(
                                                "View chart in expanded window",
                                                target=expand_id,
                                                placement="bottom",
                                            ),
                                        ],
                                        className="float-end",
                                    ),
                                    dcc.Download(id=f"download-{chart_id}"),
                                ],
                                style=card_header_style,
                            ),
                            dbc.CardBody(
                                [
                                    dcc.Graph(
                                        id=chart_id,
                                        config=chart_config,
                                        style=graph_style,
                                        figure=figure
                                        if figure is not None
                                        else {"layout": graph_layout},
                                    )
                                ],
                                style=card_body_style,
                            ),
                        ],
                        style=card_style,
                    )
                ],
                xs=12,
                sm=12,
                md=12,
                lg=12,
                className="ps-0 pe-3",
            ),
        ],
        className="mb-3 gx-2",
    )


def create_water_projections_page(app, water_projections_df):
    content = html.Div(
        [
            # Sticky sidebar wrapper
            create_water_projections_filters(water_projections_df),
            html.Div(
                [
                    # Sticky bookmark bar
                    # Desktop bookmark bar (hidden on mobile/tablet)
                    html.Div(
                        [
                            create_bookmark_bar(
                                sections,
                                data_page_parent="water_projections",
                                subnav_items=None,
                            )
                        ],
                        className="d-none d-lg-block",  # Hide on <992px, show on ≥992px
                        style={
                            "position": "fixed",
                            "top": "100px",
                            "left": "320px",
                            "right": "0",
                            "zIndex": "1000",
                            "backgroundColor": "white",
                            "padding": "8px 20px",
                            "height": "80px",
                        },
                    ),
                    # Mobile bookmark bar (hidden on desktop)
                    html.Div(
                        [
                            # Simplified mobile navigation
                            dbc.Nav(
                                [
                                    dbc.NavLink(
                                        "Water Projections",
                                        href="#water-projections-section",
                                        className="px-2",
                                    ),
                                ],
                                horizontal=True,
                                pills=True,
                                className="justify-content-center",
                            )
                        ],
                        className="d-block d-lg-none",  # Show on <992px, hide on ≥992px
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
                            # Single chart container is updated by callback
                            html.Div(id="wp-chart-container"),
                        ],
                        fluid=True,
                    ),
                ],
                style={
                    "marginLeft": "320px",  # Sidebar width (300px) + padding (20px)
                    "marginTop": "20px",
                    "padding": "20px",
                    "minHeight": "calc(100vh - 90px)",
                    "backgroundColor": "white",
                },
            ),
            # Modal for expanded view
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle(id="water-modal-title")),
                    dbc.ModalBody(
                        [
                            dcc.Graph(
                                id="water-expanded-graph",
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
                id="water-graph-modal",
                # size="xl",
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

    return create_base_layout(content)
