import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc
#from layouts.data_page_layout import create_data_page_layout
from layouts.base_layout import create_base_layout
from components.bookmark_bar import create_bookmark_bar
from components.filters.pue_wue_filters_vertical import create_pue_wue_filters


# define bookmark sections
sections = [
        #{"id": "filters", "title": "Filters"},
        {"id": "pue", "title": "PUE Data"},
        {"id": "wue", "title": "WUE Data"},
        {"id": "comparison", "title": "PUE vs WUE"}
    ]

subnav_items = [
        {"id": "pue-subnav", "title": "Methodology", "href": "/pue-wue-methodology"},
        {"id": "wue-subnav", "title": "Dataset"}
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
            "height": 600,
            "width": 1000,
            "scale": 1
        }
    }
    
    # Page layout styles
    card_header_style = {"border": 'none', "padding": "0px 15px", "marginBottom": "0px", "backgroundColor": "#ffffff"}
    card_body_style = {"border": 'none', "paddingTop": "0px", "backgroundColor": "#ffffff", "minHeight": "65vh"}
    card_style = {"border": "none", "boxShadow": "none", "height": "auto"}
    graph_style = {"height": "65vh", "width": "100%", "marginTop": "0px","paddingTop": "0px", "border": "none" }
    graph_layout = {"autosize": True, "margin": {"l": 60, "r": 120, "t": 20, "b": 60}, "height": None}
    description_style = {"textAlign": "center", "backgroundColor": "#f8f9fa", "padding": "10px", "borderRadius": "5px", "font-size": "0.8rem"}
    
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5(title, className="text-left"),
                    dbc.Button(html.I(className="fas fa-expand"), 
                        id=expand_id, 
                        size="sm", 
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
                dcc.Markdown(description_md, 
                             style=description_style,
                             mathjax=True)  # Enable LaTeX rendering
            ], className="d-flex align-items-center justify-content-center h-100")
        ], xs=12, sm=12, md=3, lg=3, className="ps-2 pe-0"),
    ], className="mb-3 gx-2")


def create_pue_wue_page(app, pue_wue_df):
    content = html.Div([ 
        # Bookmark Navigation Bar
        #create_bookmark_bar(sections),

        # #Filters section
        # html.Div([
        #     html.A(id="filters-section"),
        #     dbc.Accordion([
        #         dbc.AccordionItem([
        #             create_pue_wue_filters(pue_wue_df),
        #             html.Div(id='output-container'),
        #         ],
        #         title=html.Span([
        #             html.I(className="fas fa-filter me-2"),
        #             "Show Filters"
        #         ]),
        #         className="filter-accordion .accordion-item"
        #         ),
        #     ],
        #     flush=True,
        #     start_collapsed=True,
        #     className="filter-accordion"
        #     ),
        # ]),

        
        # Sticky sidebar wrapper
        create_pue_wue_filters(pue_wue_df),

        html.Div([
            #Sticky bookmark bar
            html.Div([
                create_bookmark_bar(sections,subnav_items)
            ], 
            style={
                # "position": "sticky",
                # "top": "0",
                # "zIndex": "1000",
                # "backgroundColor": "white",
                # "padding": "10px 0",
                # "marginBottom": "20px",
                # "marginTop": "0"
                "position": "fixed",      
                "top": "80px",            
                "left": "320px",         
                "right": "0",             
                "zIndex": "1000",
                "backgroundColor": "white",
                "padding": "8px 20px",
                "height": "80px"
            }
            ),  

        dbc.Container([
            # PUE Chart
            html.Div([
                html.A(id="pue-section"),
                create_chart_row(
                    chart_id="pue-scatter-chart",
                    title="Data Center Power Usage Effectiveness (PUE)",
                    expand_id="expand-pue",
                    description_md='''
                        ###### PUE (Power Utilization Effectiveness)

                        PUE measures the overall energy efficiency of a data center and was developed by The Green Grid organization. Since 2016, it has been standardized under ISO/IEC 30134-2. The metric provides insight into how efficiently a data center uses energy, with values closer to 1.0 indicating higher energy efficiency.

                        It is calculated using the following **formula:**

                        **PUE = Total Facility Energy / IT Equipment Energy**

                        A PUE of 1.0 represents perfect efficiency, meaning all power consumed goes directly to IT equipment with no overhead for cooling, lighting, or other facility operations.
                        ''',
                    filename="pue_chart"
                )
            ], style={"margin": "35px 0"}),

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
                
                To be updated...
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
                
                To be updated...
                ''',
                filename="pue_wue_comparison"
            )
        ]),
        
        # Summary section
        html.Div(
            id='summary',
            style={
                #"backgroundColor": "#f8f9fa",
                "font-size": "14px",
                "padding": "10px",
                "borderRadius": "5px",
                "marginTop": "20px",
            }
        ),
    ], fluid=True)
    ], style={
            "marginLeft": "320px",  # Sidebar width (300px) + padding (20px)
            "marginTop": "20px",
            "padding": "20px",
            "minHeight": "calc(100vh - 90px)",
            "backgroundColor": "white"
        }),
    
        # Modal for expanded view
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(id="modal-title")),
            dbc.ModalBody([
                dcc.Graph(id="expanded-graph", style={
                    "height": "80vh", 
                    "width": "100%"
                })
            ], style={"padding": "0"}),
        ], id="graph-modal", 
        size="xl", 
        is_open=False,
        style={
            "maxWidth": "95vw",
            "width": "95vw", 
            "margin": "2.5vh auto"
        }),
    ])

    return create_base_layout(content)