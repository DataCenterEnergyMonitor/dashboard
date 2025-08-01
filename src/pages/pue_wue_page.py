import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc
from layouts.data_page_layout import create_data_page_layout
from components.bookmark_bar import create_bookmark_bar
from components.filters.pue_wue_filters import create_pue_wue_filters

# define bookmark sections
sections = [
        {"id": "pue", "title": "PUE Trends"},
        {"id": "wue", "title": "WUE Trends"},
        {"id": "comparison", "title": "PUE vs WUE"}
    ]

def create_chart_row(chart_id, title, expand_id, description_md, filename="chart"):
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
        "modeBarButtons": [['toImage'], ['resetScale2d']],
        "displaylogo": False,
        "toImageButtonOptions": {
            "format": "png",
            "filename": filename,
            "height": 500,
            "width": 800,
            "scale": 1
        }
    }
    
    # Page layout styles
    card_header_style = {"border": 'none', "padding": "5px 15px", "backgroundColor": "#ffffff"}
    card_body_style = {"border": 'none', "padding": "10px", "backgroundColor": "#ffffff", "minHeight": "60vh"}
    card_style = {"border": "none", "boxShadow": "none", "height": "auto"}
    graph_style = {"height": "60vh", "width": "100%"}
    graph_layout = {"autosize": True, "margin": {"l": 60, "r": 120, "t": 50, "b": 60}, "height": None}
    description_style = {"textAlign": "center", "backgroundColor": "#f8f9fa", "padding": "10px", "borderRadius": "5px", "font-size": "0.8rem"}
    
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5(title, className="mb-0 text-left"),
                    dbc.Button(html.I(className="fas fa-expand"), 
                        id=expand_id, 
                        size="md", 
                        color="light", 
                        className="float-end"
                    )
                ], style=card_header_style),
                dbc.CardBody([
                    dcc.Graph(
                        id=chart_id,
                        config=chart_config,
                        style=graph_style,
                        figure={"layout": graph_layout}
                    )
                ], style=card_body_style)
            ], style=card_style)
        ], xs=12, sm=12, md=9, lg=9, className="ps-0 pe-3"),
        
        dbc.Col([
            html.Div([
                dcc.Markdown(description_md, style=description_style)
            ], className="d-flex align-items-center justify-content-center h-100")
        ], xs=12, sm=12, md=3, lg=3, className="ps-2 pe-0"),
    ], className="mb-3 gx-2")


def create_pue_wue_page(app, pue_wue_df):
    content = dbc.Container([
        # Bookmark Navigation Bar
        create_bookmark_bar(sections),

        # Filters section
        html.Div([
            html.A(id="filters-section"),
            dbc.Accordion([
                dbc.AccordionItem([
                    create_pue_wue_filters(pue_wue_df),
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
        ]),

        html.Br(),
        
        # PUE Chart
        html.Div([
            html.A(id="pue-section"),
            create_chart_row(
                chart_id="pue-scatter-chart",
                title="Data Center Power Usage Effectiveness (PUE)",
                expand_id="expand-pue",
                description_md='''
                ##### Power Utilization Effectiveness
                
                **PUE** measures how efficiently a data center uses energy.
                
                **PUE = 1.0**: Perfect efficiency (ideal)
                ''',
                filename="pue_chart"
            )
        ], style={"margin": "30px 0"}),

        html.Br(),
        
        # WUE Chart
        html.Div([
            html.A(id="wue-section"),
            create_chart_row(
                chart_id="wue-scatter-chart",
                title="Data Center Water Usage Effectiveness (WUE)",
                expand_id="expand-wue",
                description_md='''
                ##### Water Utilization Effectiveness
                
                **WUE** measures water efficiency in data centers.
                
                - **WUE = Liters/kWh** of IT energy
                - **Lower is better**
                - Varies by climate and cooling method
                
                Typical ranges: 0.5 - 3.0 L/kWh
                ''',
                filename="wue_chart"
            )
        ]),

        html.Br(),
        
        # WUE vs PUE Chart
        html.Div([
            html.A(id="comparison-section"),
            create_chart_row(
                chart_id="pue-wue-scatter-chart", 
                title="WUE vs PUE Relationship",
                expand_id="expand-pue-wue",
                description_md='''
                ##### PUE vs WUE Relationship
                
                **Correlation Analysis** between power and water efficiency.
                
                - **Positive correlation**: Higher PUE → Higher WUE
                - **Climate impact**: Hot climates increase both metrics
                
                Optimal: Low PUE + Low WUE
                ''',
                filename="pue_wue_comparison"
            )
        ]),
        
        # Summary section
        html.Div(
            id='summary',
            style={
                "backgroundColor": "#f8f9fa",
                "padding": "10px",
                "borderRadius": "5px",
                "marginTop": "20px",
            }
        ),
        
        # Modal for expanded view
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(id="modal-title")),
            dbc.ModalBody([
                dcc.Graph(id="expanded-graph", style={"height": "70vh"})
            ], style={"padding": "0"}),
        ], id="graph-modal", size="xl", is_open=False),
    ])

    return create_data_page_layout(content)