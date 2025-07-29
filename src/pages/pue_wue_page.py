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
            dbc.Row([
                # First row - chart takes more space, starts at left edge
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Data Center Power Usage Effectiveness (PUE)", className="mb-0 text-center"),
                            dbc.Button(html.I(className="fas fa-expand"), 
                                id="expand-pue", 
                                size="md", 
                                color="light", 
                                className="float-end"
                            )
                        ], style={"border": 'none', "padding": "5px 15px", "backgroundColor": "#ffffff"}),
                        dbc.CardBody([
                            dcc.Graph(
                                id="pue-scatter-chart",
                                config={"responsive": True, "displayModeBar": True},
                                figure={
                                    "layout": {
                                        "margin": {"l": 20, "r": 20, "t": 40, "b": 40}  # Minimal margins
                                    }
                                }
                            )
                        ], style={"border": 'none', "padding": "0px", "backgroundColor": "#ffffff"})
                    ],style={"border": "none", "boxShadow": "none"})
                ], xs=12, sm=12, md=9, lg=9, className="ps-0 pe-3"),  # More space, no left padding
                
                dbc.Col([
                    html.Div([
                        dcc.Markdown('''
                        ##### Power Utilization Effectiveness

                        Dash supports [Markdown](http://commonmark.org/help).

                        Markdown is a simple way to write and format text.
                        It includes a syntax for things like **bold text** and *italics*,
                        [links](http://commonmark.org/help), inline `code` snippets, lists,
                        quotes, and more.
                        ''', style={"textAlign": "center", "backgroundColor": "#f8f9fa", "padding": "10px", "borderRadius": "5px"})
                    ], className="d-flex align-items-center justify-content-center h-100")
                ], xs=12, sm=12, md=3, lg=3, className="ps-2 pe-0"),
            ], className="mb-3 gx-2"),
            html.Br(),
            dbc.Row([
                # First row - chart takes more space, starts at left edge
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("Data Center Water Usage Effectiveness (WUE)", className="mb-0 text-center"),
                            dbc.Button(html.I(className="fas fa-expand"), 
                                id="expand-wue", 
                                size="md", 
                                color="light", 
                                className="float-end"
                            )
                        ], style={"border": 'none', "padding": "5px 15px", "backgroundColor": "#ffffff"}),
                        dbc.CardBody([
                            dcc.Graph(
                                id="pue-scatter-chart",
                                config={"responsive": True, "displayModeBar": True},
                                figure={
                                    "layout": {
                                        "margin": {"l": 20, "r": 20, "t": 40, "b": 40}  # Minimal margins
                                    }
                                }
                            )
                        ], style={"border": 'none', "padding": "0px", "backgroundColor": "#ffffff"})
                    ],style={"border": "none", "boxShadow": "none"})
                ], xs=12, sm=12, md=9, lg=9, className="ps-0 pe-3"),  # More space, no left padding
                html.Br(),
                dbc.Col([
                    html.Div([
                        dcc.Markdown('''
                        ##### Water Utilization Effectiveness

                        Dash supports [Markdown](http://commonmark.org/help).

                        Markdown is a simple way to write and format text.
                        It includes a syntax for things like **bold text** and *italics*,
                        [links](http://commonmark.org/help), inline `code` snippets, lists,
                        quotes, and more.
                        ''', style={"textAlign": "center", "backgroundColor": "#f8f9fa"})
                    ], className="d-flex align-items-center justify-content-center h-100")
                ], xs=12, sm=12, md=3, lg=3, className="ps-2 pe-0"),
            ], className="mb-3 gx-2"),
                        dbc.Row([
                # First row - chart takes more space, starts at left edge
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5("WUE vs PUE", className="mb-0 text-center"),
                            dbc.Button(html.I(className="fas fa-expand"), 
                                id="expand-pue-wue", 
                                size="md", 
                                color="light", 
                                className="float-end"
                            )
                        ], style={"border": 'none', "padding": "5px 15px", "backgroundColor": "#ffffff"}),
                        dbc.CardBody([
                            dcc.Graph(
                                id="pue-scatter-chart",
                                config={"responsive": True, "displayModeBar": True},
                                figure={
                                    "layout": {
                                        "margin": {"l": 20, "r": 20, "t": 40, "b": 40}  # Minimal margins
                                    }
                                }
                            )
                        ], style={"border": 'none', "padding": "0px", "backgroundColor": "#ffffff"})
                    ],style={"border": "none", "boxShadow": "none"})
                ], xs=12, sm=12, md=9, lg=9, className="ps-0 pe-3"),  # More space, no left padding
                
                dbc.Col([
                    html.Div([
                        dcc.Markdown('''
                        ##### WUE vs PUE Relationship

                        Dash supports [Markdown](http://commonmark.org/help).

                        Markdown is a simple way to write and format text.
                        It includes a syntax for things like **bold text** and *italics*,
                        [links](http://commonmark.org/help), inline `code` snippets, lists,
                        quotes, and more.
                        ''', style={"textAlign": "center", "backgroundColor": "#f8f9fa"})
                    ], className="d-flex align-items-center justify-content-center h-100")
                ], xs=12, sm=12, md=3, lg=3, className="ps-2 pe-0"),
            ], className="mb-3 gx-2"),
                # Modal for expanded view
            dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(id="modal-title")),
            dbc.ModalBody([
                dcc.Graph(id="expanded-graph", style={"height": "70vh"})
            ], style={"padding": "0"}),
        ], id="graph-modal", size="xl", is_open=False),
        ]
    )

    return create_data_page_layout(content)  # Use the base layout