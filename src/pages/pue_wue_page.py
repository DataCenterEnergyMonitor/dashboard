import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc
from layouts.data_page_layout import create_data_page_layout
# from components.filters.pue_wue_filters import create_filters
from components.filters.pue_wue_filters import create_pue_wue_filters


def create_pue_wue_page(app, pue_df, wue_df):
    content = dbc.Container(
        [
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            create_pue_wue_filters(pue_df),
                            html.Div(id='output-container'),
                        ],
                        title=html.Span([
                            html.I(className="fas fa-filter me-2"),
                            "Filters"
                        ]),
                        className="filter-accordion .accordion-item"
                    ),
                ],
                flush=True,
                start_collapsed=True,
                className="filter-accordion"
            ),

            # Charts section
            dbc.Row(
                [
                    # First row - two charts side by side
                    dbc.Col(
                        [
                            dcc.Graph(
                                id="pue-scatter-chart",
                                #style={"height": "400px"},
                                config={"responsive": True}
                            )
                        ],
                        xs=12, sm=12, md=6, lg=6
                    ),  # Takes half width on medium+ screens

                    dbc.Col(
                        [
                            dcc.Graph(
                                id="wue-scatter-chart",
                                #style={"height": "400px"},
                                config={"responsive": True}
                            )
                        ],
                        xs=12, sm=12, md=6, lg=6
                    ),  # Takes half width on medium+ screens
                ],
                className="mb-4"
            ),

            dbc.Row(
                [
                    # Second row - one chart full width
                    dbc.Col(
                        [
                            dcc.Graph(
                                id="combined-chart",
                                #style={"height": "500px"},
                                config={"responsive": True}
                            )
                        ],
                        xs=12, sm=12, md=6, lg=6,
                        className="mx-auto"
                    ),  # Full width
                ],
                className = "justify-content-center"
            ),
        ]
    )

    return create_data_page_layout(content)  # Use the base layout