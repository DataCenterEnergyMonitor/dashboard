from dash import dcc, html
import dash_bootstrap_components as dbc

def create_figure_card(
    fig_id,
    title,
    expand_id,
    accordion_children=None,
    accordion_title=None,
    filename="figure",
    figure=None,
    show_modebar=True,
):
    """
    Create a standardized figure row with consistent styling

    Args:
        fig_id: ID for the figure component
        title: Chart title for header
        expand_id: ID for expand button
        accordion_children: Optional accordion content
        accordion_title: Optional accordion title
        filename: Filename for image download
        figure: Plotly figure object
        show_modebar: If False, hides the modebar (default True)
    """

    # Chart config
    fig_config = {
        "responsive": True,
        "displayModeBar": show_modebar,
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
    fig_style = {
        "height": "65vh",
        "width": "100%",
        "marginTop": "0px",
        "paddingTop": "0px",
        "border": "none",
    }
    fig_layout = {
        "autosize": True,
        "margin": {"l": 60, "r": 120, "t": 20, "b": 60},
        "height": None,
    }

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
                                                id=f"download-btn-{fig_id}",
                                                size="sm",
                                                color="light",
                                                className="me-2",
                                                title="Download figure data",
                                            ),
                                            dbc.Tooltip(
                                                "Download figure data as Excel file",
                                                target=f"download-btn-{fig_id}",
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
                                                title="Expand figure",
                                            ),
                                            dbc.Tooltip(
                                                "View figure in expanded window",
                                                target=expand_id,
                                                placement="bottom",
                                            ),
                                        ],
                                        className="float-end",
                                    ),
                                    dcc.Download(id=f"download-{fig_id}"),
                                ],
                                style=card_header_style,
                            ),
                            dbc.CardBody(
                                [
                                    dcc.Graph(
                                        id=fig_id,
                                        config=fig_config,
                                        style=fig_style,
                                        figure=figure
                                        if figure is not None
                                        else {"layout": fig_layout},
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

