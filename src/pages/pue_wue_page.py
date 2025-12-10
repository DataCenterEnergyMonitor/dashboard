import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc

# from layouts.data_page_layout import create_data_page_layout
from layouts.base_layout import create_base_layout
from components.bookmark_bar import create_bookmark_bar
from components.filters.pue_wue_filters_vertical import create_pue_wue_filters


# define bookmark sections
sections = [
    # {"id": "filters", "title": "Filters"},
    {"id": "pue", "title": "PUE Data"},
    {"id": "wue", "title": "WUE Data"},
    {"id": "comparison", "title": "PUE vs WUE"},
    {"id": "trends", "title": "Reporting Trends"},
]

subnav_items = [
    {"id": "pue-subnav", "title": "PUE", "href": "/pue-methodology"},
    {"id": "wue-subnav", "title": "WUE", "href": "/wue-methodology"},
    {"id": "wue-subnav", "title": "Dataset"},
]

# def create_chart_row(chart_id, title, expand_id, accordion_children=None, accordion_title=None, filename="chart", scrollable=False):
#     """
#     Create a standardized chart row with consistent styling

#     Args:
#         chart_id: ID for the graph component
#         title: Chart title for header
#         expand_id: ID for expand button
#         description_md: Markdown description for right column
#         filename: Filename for image download
#         scrollable: If True, makes the chart container scrollable
#     """
#     if scrollable:
#         card_body_style = {
#             "border": 'none',
#             "paddingTop": "0px",
#             "backgroundColor": "#ffffff",
#             "height": "65vh",  # Fixed height
#             "overflowY": "auto",  # Enable vertical scroll
#             "overflowX": "hidden"  # Prevent horizontal scroll
#         }
#         graph_style = {
#             "height": "auto",  # Let graph expand to full content height
#             "minHeight": "65vh",  # Minimum height matches container
#             "width": "100%",
#             "marginTop": "0px",
#             "paddingTop": "0px",
#             "border": "none"
#         }
#     else:
#         card_body_style = {
#                 "border": 'none',
#                 "paddingTop": "0px",
#                 "backgroundColor": "#ffffff",
#                 "minHeight": "65vh"
#             }
#         graph_style = {
#                 "height": "65vh",
#                 "width": "100%",
#                 "marginTop": "0px",
#                 "paddingTop": "0px",
#                 "border": "none"
#             }

#     # Chart config
#     chart_config = {
#         "responsive": True,
#         "displayModeBar": True,
#         "modeBarButtons": [['toImage'], ['zoomIn2d'], ['zoomOut2d'], ['pan2d'],['autoScale2d']],
#         "displaylogo": False,
#         "toImageButtonOptions": {
#             "format": "png",
#             "filename": filename,
#             "height": 700,
#             "width": 1200,
#             "scale": 1
#         }
#     }

#     # Page layout styles
#     card_header_style = {"border": 'none', "padding": "8px 15px", "marginBottom": "0px", "backgroundColor": "#ffffff"}
#     card_body_style = {"border": 'none', "paddingTop": "0px", "backgroundColor": "#ffffff", "minHeight": "65vh"}
#     card_style = {"border": "none", "boxShadow": "none", "height": "auto"}
#     graph_style = {"height": "65vh", "width": "100%", "marginTop": "0px","paddingTop": "0px", "border": "none" }
#     graph_layout = {"autosize": True, "margin": {"l": 60, "r": 120, "t": 20, "b": 60}, "height": None}
#     #description_style = {"textAlign": "center", "backgroundColor": "#f8f9fa", "padding": "10px", "borderRadius": "5px", "font-size": "0.8rem"}

#     # if accordion_children:
#     accordion_element = html.Div(
#             dbc.Accordion(
#                 [
#                     dbc.AccordionItem(
#                         children=accordion_children,
#                         title=accordion_title,
#                     ),
#                 ],
#                 flush=True,
#                 start_collapsed=True,
#                 className="filter-accordion",
#                 style={"width": "80%"},
#             ),
#         )
#     # else:
#     #     accordion_element = None

#     return dbc.Row([
#         dbc.Col([
#             dbc.Card([
#                 dbc.CardHeader([
#                     html.H5(title, className="text-left"),
#                 accordion_element if accordion_children else None,
#                 html.Div([
#                     dbc.Button([
#                         html.I(className="fas fa-download",
#                             style={"marginRight": "6px"}),
#                             html.Span("Data .xlsx",
#                                         style={"fontSize": "0.8rem"})
#                     ],
#                         id=f"download-btn-{chart_id}",
#                         size="sm",
#                         color="light",
#                         className="me-2",
#                         title="Download chart data"
#                     ),
#                     dbc.Tooltip(
#                             "Download chart data as Excel file",
#                             target=f"download-btn-{chart_id}",
#                             placement="bottom"
#                         ),
#                     dbc.Button([
#                         html.I(className="fas fa-expand",
#                             style={"marginRight": "6px"}),
#                             html.Span("Expand",
#                                         style={"fontSize": "0.8rem"})
#                     ],
#                         id=expand_id,
#                         size="sm",
#                         color="light",
#                         title="Expand chart"
#                     ),
#                     dbc.Tooltip(
#                             "View chart in expanded window",
#                             target=expand_id,
#                             placement="bottom"
#                         ),
#                 ], className="float-end",
#                 #style={"marginRight": "50px"}
#                 ),

#                 dcc.Download(id=f"download-{chart_id}")
#                 ], style=card_header_style),
#                 #accordion_element if accordion_children else None,
#                 dbc.CardBody([
#                     dcc.Graph(
#                         id=chart_id,
#                         config=chart_config,
#                         style=graph_style,
#                         figure={"layout": graph_layout}
#                     )
#                 ], style=card_body_style)
#             ], style=card_style)
#         ], xs=12, sm=12, md=12, lg=12, className="ps-0 pe-3"),

#     ], className="mb-3 gx-2")
# def create_chart_row(chart_id, title, expand_id, accordion_children=None, accordion_title=None, filename="chart", scrollable=False):
#     """
#     Create a standardized chart row with consistent styling

#     Args:
#         chart_id: ID for the graph component
#         title: Chart title for header
#         expand_id: ID for expand button
#         description_md: Markdown description for right column
#         filename: Filename for image download
#         scrollable: If True, makes the chart container scrollable
#     """

#     # Chart config
#     chart_config = {
#         "responsive": True,
#         "displayModeBar": True,
#         "modeBarButtons": [['toImage'], ['zoomIn2d'], ['zoomOut2d'], ['pan2d'],['autoScale2d']],
#         "displaylogo": False,
#         "toImageButtonOptions": {
#             "format": "png",
#             "filename": filename,
#             "height": 700,
#             "width": 1200,
#             "scale": 1
#         }
#     }

#     # Page layout styles - CONDITIONAL based on scrollable flag
#     card_header_style = {"border": 'none', "padding": "8px 15px", "marginBottom": "0px", "backgroundColor": "#ffffff"}
#     card_style = {"border": "none", "boxShadow": "none", "height": "auto"}

#     if scrollable:
#         card_body_style = {
#             "border": 'none',
#             "paddingTop": "0px",
#             "backgroundColor": "#ffffff",
#             "height": "65vh",  # Fixed height
#             "maxHeight": "65vh",  # Enforce max height
#             "overflowY": "auto",  # Enable vertical scroll
#             "overflowX": "hidden"  # Prevent horizontal scroll
#         }
#         graph_style = {
#             "height": "auto",  # Let graph expand to full content height
#             "minHeight": "65vh",  # Minimum height matches container
#             "width": "100%",
#             "marginTop": "0px",
#             "paddingTop": "0px",
#             "border": "none"
#         }
#         graph_layout = {"autosize": False, "margin": {"l": 150, "r": 50, "t": 20, "b": 60}, "height": None}
#     else:
#         card_body_style = {
#             "border": 'none',
#             "paddingTop": "0px",
#             "backgroundColor": "#ffffff",
#             "minHeight": "65vh"
#         }
#         graph_style = {
#             "height": "65vh",
#             "width": "100%",
#             "marginTop": "0px",
#             "paddingTop": "0px",
#             "border": "none"
#         }
#         graph_layout = {"autosize": True, "margin": {"l": 60, "r": 120, "t": 20, "b": 60}, "height": None}

#     # Accordion element
#     accordion_element = html.Div(
#         dbc.Accordion(
#             [
#                 dbc.AccordionItem(
#                     children=accordion_children,
#                     title=accordion_title,
#                 ),
#             ],
#             flush=True,
#             start_collapsed=True,
#             className="filter-accordion",
#             style={"width": "80%"},
#         ),
#     ) if accordion_children else None

#     return dbc.Row([
#         dbc.Col([
#             dbc.Card([
#                 dbc.CardHeader([
#                     html.H5(title, className="text-left"),
#                     accordion_element,
#                     html.Div([
#                         dbc.Button([
#                             html.I(className="fas fa-download",
#                                 style={"marginRight": "6px"}),
#                                 html.Span("Data .xlsx",
#                                             style={"fontSize": "0.8rem"})
#                         ],
#                             id=f"download-btn-{chart_id}",
#                             size="sm",
#                             color="light",
#                             className="me-2",
#                             title="Download chart data"
#                         ),
#                         dbc.Tooltip(
#                                 "Download chart data as Excel file",
#                                 target=f"download-btn-{chart_id}",
#                                 placement="bottom"
#                             ),
#                         dbc.Button([
#                             html.I(className="fas fa-expand",
#                                 style={"marginRight": "6px"}),
#                                 html.Span("Expand",
#                                             style={"fontSize": "0.8rem"})
#                         ],
#                             id=expand_id,
#                             size="sm",
#                             color="light",
#                             title="Expand chart"
#                         ),
#                         dbc.Tooltip(
#                                 "View chart in expanded window",
#                                 target=expand_id,
#                                 placement="bottom"
#                             ),
#                     ], className="float-end"),

#                     dcc.Download(id=f"download-{chart_id}")
#                 ], style=card_header_style),
#                 dbc.CardBody([
#                     dcc.Graph(
#                         id=chart_id,
#                         config=chart_config,
#                         style=graph_style,
#                         figure={"layout": graph_layout}
#                     )
#                 ], style=card_body_style)
#             ], style=card_style)
#         ], xs=12, sm=12, md=12, lg=12, className="ps-0 pe-3"),

#     ], className="mb-3 gx-2")

# def create_chart_row(chart_id, title, expand_id, accordion_children=None, accordion_title=None, filename="chart", scrollable=False, sticky_header=False):
#     """
#     Create a standardized chart row with consistent styling

#     Args:
#         chart_id: ID for the graph component
#         title: Chart title for header
#         expand_id: ID for expand button
#         description_md: Markdown description for right column
#         filename: Filename for image download
#         scrollable: If True, makes the chart container scrollable
#         sticky_header: If True, allows to scroll along y-axis while keeping x-axis and legend sticky (applies to heatmaps)
#     """

#     # Chart config
#     chart_config = {
#         "responsive": True,
#         "displayModeBar": True,
#         "modeBarButtons": [['toImage'], ['zoomIn2d'], ['zoomOut2d'], ['pan2d'],['autoScale2d']],
#         "displaylogo": False,
#         "toImageButtonOptions": {
#             "format": "png",
#             "filename": filename,
#             "height": 700,
#             "width": 1200,
#             "scale": 1
#         }
#     }

#     # Page layout styles
#     card_header_style = {"border": 'none', "padding": "8px 15px", "marginBottom": "0px", "backgroundColor": "#ffffff"}
#     card_style = {"border": "none", "boxShadow": "none", "height": "auto"}

#     if sticky_header and scrollable:
#         # Special layout for heatmaps with sticky header
#         card_body_style = {
#             "border": 'none',
#             "paddingTop": "0px",
#             "backgroundColor": "#ffffff",
#             "height": "65vh",
#             "display": "flex",
#             "flexDirection": "column"
#         }

#         # Sticky header section (legend + x-axis)
#         header_section = html.Div([
#             html.Div(id=f"{chart_id}-legend", style={
#                 "position": "sticky",
#                 "top": "0",
#                 "backgroundColor": "white",
#                 "zIndex": "100",
#                 "padding": "10px 0",
#                 "borderBottom": "1px solid #e0e0e0"
#             })
#         ])

#         # Scrollable graph section
#         graph_section = html.Div([
#             dcc.Graph(
#                 id=chart_id,
#                 config=chart_config,
#                 style={
#                     "height": "auto",
#                     "minHeight": "calc(65vh - 120px)",
#                     "width": "100%",
#                     "marginTop": "0px",
#                     "paddingTop": "0px",
#                     "border": "none"
#                 },
#                 figure={"layout": {"autosize": False, "margin": {"l": 150, "r": 50, "t": 20, "b": 60}, "height": None}}
#             )
#         ], style={
#             "overflowY": "auto",
#             "overflowX": "hidden",
#             "flex": "1"
#         })

#         graph_content = html.Div([header_section, graph_section], style={"height": "100%", "display": "flex", "flexDirection": "column"})

#     elif scrollable:
#         card_body_style = {
#             "border": 'none',
#             "paddingTop": "0px",
#             "backgroundColor": "#ffffff",
#             "height": "65vh",
#             "maxHeight": "65vh",
#             "overflowY": "auto",
#             "overflowX": "hidden"
#         }
#         graph_content = dcc.Graph(
#             id=chart_id,
#             config=chart_config,
#             style={
#                 "height": "auto",
#                 "minHeight": "65vh",
#                 "width": "100%",
#                 "marginTop": "0px",
#                 "paddingTop": "0px",
#                 "border": "none"
#             },
#             figure={"layout": {"autosize": False, "margin": {"l": 150, "r": 50, "t": 20, "b": 60}, "height": None}}
#         )
#     else:
#         card_body_style = {
#             "border": 'none',
#             "paddingTop": "0px",
#             "backgroundColor": "#ffffff",
#             "minHeight": "65vh"
#         }
#         graph_content = dcc.Graph(
#             id=chart_id,
#             config=chart_config,
#             style={
#                 "height": "65vh",
#                 "width": "100%",
#                 "marginTop": "0px",
#                 "paddingTop": "0px",
#                 "border": "none"
#             },
#             figure={"layout": {"autosize": True, "margin": {"l": 60, "r": 120, "t": 20, "b": 60}, "height": None}}
#         )

#     accordion_element = html.Div(
#         dbc.Accordion(
#             [
#                 dbc.AccordionItem(
#                     children=accordion_children,
#                     title=accordion_title,
#                 ),
#             ],
#             flush=True,
#             start_collapsed=True,
#             className="filter-accordion",
#             style={"width": "80%"},
#         ),
#     ) if accordion_children else None

#     return dbc.Row([
#         dbc.Col([
#             dbc.Card([
#                 dbc.CardHeader([
#                     html.H5(title, className="text-left"),
#                     accordion_element,
#                     html.Div([
#                         dbc.Button([
#                             html.I(className="fas fa-download", style={"marginRight": "6px"}),
#                             html.Span("Data .xlsx", style={"fontSize": "0.8rem"})
#                         ],
#                             id=f"download-btn-{chart_id}",
#                             size="sm",
#                             color="light",
#                             className="me-2",
#                             title="Download chart data"
#                         ),
#                         dbc.Tooltip(
#                             "Download chart data as Excel file",
#                             target=f"download-btn-{chart_id}",
#                             placement="bottom"
#                         ),
#                         dbc.Button([
#                             html.I(className="fas fa-expand", style={"marginRight": "6px"}),
#                             html.Span("Expand", style={"fontSize": "0.8rem"})
#                         ],
#                             id=expand_id,
#                             size="sm",
#                             color="light",
#                             title="Expand chart"
#                         ),
#                         dbc.Tooltip(
#                             "View chart in expanded window",
#                             target=expand_id,
#                             placement="bottom"
#                         ),
#                     ], className="float-end"),
#                     dcc.Download(id=f"download-{chart_id}")
#                 ], style=card_header_style),
#                 dbc.CardBody(graph_content, style=card_body_style)
#             ], style=card_style)
#         ], xs=12, sm=12, md=12, lg=12, className="ps-0 pe-3"),
#     ], className="mb-3 gx-2")


def create_chart_row(
    chart_id,
    title,
    expand_id,
    accordion_children=None,
    accordion_title=None,
    filename="chart",
    scrollable=False,
    dual_chart=False,
):
    """
    Create a standardized chart row with consistent styling

    Args:
        scrollable: If True, makes the chart container scrollable
        dual_chart: If True, creates header chart + scrollable chart overlay
    """

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

    card_header_style = {
        "border": "none",
        "padding": "8px 15px",
        "marginBottom": "0px",
        "backgroundColor": "#ffffff",
    }
    card_style = {"border": "none", "boxShadow": "none", "height": "auto"}

    accordion_element = (
        html.Div(
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
        if accordion_children
        else None
    )

    if dual_chart and scrollable:
        # Wrap everything in a container with fixed modebar OUTSIDE scroll
        card_body_content = html.Div(
            [
                # Container for sticky header + scrollable content
                html.Div(
                    [
                        # Sticky header (legend + x-axis)
                        html.Div(
                            [
                                dcc.Graph(
                                    id=f"{chart_id}-header",
                                    config={
                                        **chart_config,
                                        "displayModeBar": False,
                                    },  # Already hidden
                                    style={
                                        "height": "180px",
                                        "width": "100%",
                                        "marginBottom": "0px",
                                    },
                                )
                            ],
                            style={
                                "position": "sticky",
                                "top": "0px",  # Changed from 40px
                                "backgroundColor": "white",
                                "zIndex": "50",
                            },
                        ),
                        # Scrollable main chart
                        html.Div(
                            [
                                dcc.Graph(
                                    id=chart_id,
                                    config={
                                        **chart_config,
                                        "displayModeBar": False,
                                    },  # HIDE modebar for heatmap
                                    style={"height": "auto", "width": "100%"},
                                )
                            ],
                            style={
                                "overflowY": "auto",
                                "overflowX": "hidden",
                                "maxHeight": "calc(65vh - 180px)",  # Adjust since we removed modebar space
                            },
                        ),
                    ],
                    style={"position": "relative"},
                )
            ]
        )

        card_body_style = {
            "border": "none",
            "paddingTop": "0px",
            "backgroundColor": "#ffffff",
            "height": "auto",
        }

    elif scrollable:
        card_body_style = {
            "border": "none",
            "paddingTop": "0px",
            "backgroundColor": "#ffffff",
            "height": "65vh",
            "maxHeight": "65vh",
            "overflowY": "auto",
            "overflowX": "hidden",
        }
        card_body_content = dcc.Graph(
            id=chart_id,
            config=chart_config,
            style={
                "height": "auto",
                "minHeight": "65vh",
                "width": "100%",
                "paddingTop": "45px",
            },
        )
    else:
        card_body_style = {
            "border": "none",
            "paddingTop": "0px",
            "backgroundColor": "#ffffff",
            "minHeight": "65vh",
        }
        card_body_content = dcc.Graph(
            id=chart_id,
            config=chart_config,
            style={"height": "65vh", "width": "100%", "paddingTop": "45px"},
        )

    return dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                [
                                    html.H5(title, className="text-left"),
                                    accordion_element,
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
                            dbc.CardBody(card_body_content, style=card_body_style),
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


def create_pue_wue_page(app, pue_wue_df):
    content = html.Div(
        [
            # Sticky sidebar wrapper
            create_pue_wue_filters(pue_wue_df),
            html.Div(
                [
                    # Sticky bookmark bar
                    # Desktop bookmark bar (hidden on mobile/tablet)
                    html.Div(
                        [
                            create_bookmark_bar(
                                sections, data_page_parent="pue_wue", subnav_items=None
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
                                        "PUE", href="#pue-section", className="px-2"
                                    ),
                                    dbc.NavLink(
                                        "WUE", href="#wue-section", className="px-2"
                                    ),
                                    dbc.NavLink(
                                        "Compare",
                                        href="#comparison-section",
                                        className="px-2",
                                    ),
                                    dbc.NavLink(
                                        "Reporting Trends",
                                        href="#trends-section",
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
                            "top": "90px",
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
                            # PUE Chart
                            html.Div(
                                [
                                    html.A(id="pue-section"),
                                    create_chart_row(
                                        chart_id="pue-scatter-chart",
                                        title="Data Center Power Usage Effectiveness (PUE)",
                                        expand_id="expand-pue",
                                        accordion_children=[
                                            dcc.Markdown(
                                                """
                                        PUE measures the overall energy efficiency of a data center and was developed by The Green Grid organization.
                                        Since 2016, it has been standardized under ISO/IEC 30134-2. The metric provides insight into how efficiently a data center uses energy, with values closer to 1.0 indicating higher energy efficiency. It is calculated using the following formula:
                                        """
                                            ),
                                            dcc.Markdown(
                                                "$\\mathrm{PUE} = \\frac{\\text{Total Facility Energy}}{\\text{IT Equipment Energy}}$",
                                                mathjax=True,
                                                style={"font-size": "14pt"},
                                            ),
                                            dcc.Markdown(
                                                """
                                        A PUE of 1.0 represents perfect efficiency, meaning all power consumed goes directly to IT equipment with no overhead for cooling, lighting, or other facility operations.
                                        """
                                            ),
                                        ],
                                        accordion_title=html.Span(
                                            [
                                                "What Does PUE Tell Us?",
                                                html.Span(
                                                    " Read more...",
                                                    className="text-link",
                                                ),
                                            ]
                                        ),
                                        filename="pue_chart",
                                    ),
                                ],
                                style={"margin": "35px 0"},
                            ),
                            html.Br(),
                            # WUE Chart
                            html.Div(
                                [
                                    html.A(id="wue-section"),
                                    create_chart_row(
                                        chart_id="wue-scatter-chart",
                                        title="Data Center Water Usage Effectiveness (WUE)",
                                        expand_id="expand-wue",
                                        accordion_children=[
                                            dcc.Markdown(
                                                """
                                    WUE (Water Usage Effectiveness) measures the overall water utilization efficiency of a data center and was developed by The Green Grid organization.
                                    Since 2016, it has been standardized under ISO/IEC 30134-4. The metric provides insight into how efficiently a data center uses water, with lower values indicating higher water efficiency. It is calculated using the following formula:
                                    """
                                            ),
                                            dcc.Markdown(
                                                "$\\mathrm{WUE} = \\frac{\\text{Total Facility Water Usage (liters)}}{\\text{IT Equipment Energy Usage (kWh)}}$",
                                                mathjax=True,
                                                style={"font-size": "14pt"},
                                            ),
                                            dcc.Markdown(
                                                """
                                    A lower WUE value indicates that less water is used per unit of IT energy consumed, reflecting more efficient water usage. WUE accounts for all water used onsite, including cooling, humidification, and other facility operations.
                                    """
                                            ),
                                        ],
                                        accordion_title=html.Span(
                                            [
                                                "What Does WUE Tell Us?",
                                                html.Span(
                                                    " Read more...",
                                                    className="text-link",
                                                ),
                                            ]
                                        ),
                                        filename="wue_chart",
                                    ),
                                ]
                            ),
                            html.Br(),
                            # WUE vs PUE Chart
                            html.Div(
                                [
                                    html.A(id="comparison-section"),
                                    create_chart_row(
                                        chart_id="pue-wue-scatter-chart",
                                        title="WUE vs PUE Relationship",
                                        expand_id="expand-pue-wue",
                                        accordion_children=[
                                            dcc.Markdown(
                                                """
                                    In progress
                                    """
                                            ),
                                        ],
                                        accordion_title=html.Span(
                                            [
                                                "What Does the WUE-PUE Relationship Tell Us?",
                                                html.Span(
                                                    " Read more...",
                                                    className="text-link",
                                                ),
                                            ]
                                        ),
                                        filename="pue_wue_comparison",
                                    ),
                                ]
                            ),
                            html.Br(),
                            #     html.Div([
                            #     html.A(id="trends-section"),
                            #     create_chart_row(
                            #         chart_id="pue-trends-chart",
                            #         title="PUE Reporting Trends Over Time",
                            #         expand_id="expand-pue-trends",
                            #         accordion_children = [
                            #                         dcc.Markdown(
                            #                             """
                            #                             TBD
                            #                             """
                            #                         ),
                            #             ],
                            #             accordion_title=html.Span([
                            #                 "Reporting Trends",
                            #                 html.Span(" Read more...", className="text-link"),
                            #             ]),
                            #         filename="pue_wue_companies",
                            #         scrollable=True
                            #     )
                            # ]),
                            html.Div(
                                [
                                    html.A(id="trends-section"),
                                    create_chart_row(
                                        chart_id="pue-trends-chart",
                                        title="PUE Reporting by Company Over Time",
                                        expand_id="expand-pue-trends",
                                        accordion_children=[dcc.Markdown("TBD")],
                                        accordion_title=html.Span(
                                            [
                                                "PUE Reporting Trends",
                                                html.Span(
                                                    " Read more...",
                                                    className="text-link",
                                                ),
                                            ]
                                        ),
                                        filename="pue_wue_companies",
                                        scrollable=True,
                                        dual_chart=True,  # Enable dual chart mode
                                    ),
                                ]
                            ),
                            html.Br(),
                            # WUE Trends Chart
                            html.Div(
                                [
                                    html.A(id="wue-trends-section"),
                                    create_chart_row(
                                        chart_id="wue-trends-chart",
                                        title="WUE Reporting by Company Over Time",
                                        expand_id="expand-wue-trends",
                                        accordion_children=[dcc.Markdown("TBD")],
                                        accordion_title=html.Span(
                                            [
                                                "WUE Reporting Trends",
                                                html.Span(
                                                    " Read more...",
                                                    className="text-link",
                                                ),
                                            ]
                                        ),
                                        filename="pue_wue_companies",
                                        scrollable=True,
                                        dual_chart=True,  # Enable dual chart mode
                                    ),
                                ]
                            ),
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
                    dbc.ModalHeader(dbc.ModalTitle(id="modal-title")),
                    dbc.ModalBody(
                        [
                            dcc.Graph(
                                id="expanded-graph",
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
                id="graph-modal",
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
