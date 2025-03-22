from dash import html, dcc
import dash_bootstrap_components as dbc
from components.filter_manager import FilterManager, FilterConfig
from components.navbar import create_navbar
from components.filter_panel import create_filter_panel
from layouts.base_layout import create_base_layout

def create_wue_page(app, wue_df, company_counts):
    # Define WUE-specific filters with dependencies
    wue_filters = [
        FilterConfig(
            id="facility_scope",
            label="Facility Scope",
            column="facility_scope",
            multi=False,
            default_value="Fleet-wide",
            show_all=False,
            depends_on=None
        ),
        FilterConfig(
            id="company",
            label="Company",
            column="company",
            multi=True,
            default_value="All",
            show_all=True,
            depends_on=["facility_scope"]
        )
    ]
    
    # Initialize WUE-specific filter manager
    wue_filter_manager = FilterManager(app, "wue", wue_df, wue_filters)

    # Get filter components without download button
    filter_components = wue_filter_manager.create_filter_components()
    
    # Extract download button and component
    download_button = html.Button(
        "Download Data",
        id=f"wue-download-button",
        style={
            'backgroundColor': '#4CAF50',
            'color': 'white',
            'padding': '8px 16px',
            'border': 'none',
            'borderRadius': '4px',
            'cursor': 'pointer',
            'fontFamily': 'Roboto, sans-serif',
            'fontWeight': '500',
            'fontSize': '14px'
        }
    )
    download_component = dcc.Download(id=f"wue-download-data")
    
    content = html.Div([
        # Main content container
        html.Div([
            # Left side - Filter Panel
            html.Div([
                create_filter_panel(filter_components)
            ], style={
                'width': '260px',
                'flexShrink': '0'
            }),

            # Right side - Main Content
            html.Div([
                html.H1(
                    "Data Center Water Usage Effectiveness (WUE): Trends by Company",
                    style={
                        'fontFamily': 'Roboto, sans-serif', 
                        'fontWeight': '500', 
                        'marginBottom': '30px',
                        'fontSize': '32px',
                        'paddingTop': '0px'
                        }
                ),
                html.Div([
                    html.P([
                        "Water Usage Effectiveness (WUE) measures the water efficiency of data centers.",
                        html.Br(),
                        "Lower WUE values indicate better water efficiency."
                    ], style={
                        'fontFamily': 'Roboto, sans-serif',
                        'marginBottom': '20px',
                        'color': '#404040',
                        'maxWidth': '800px',
                        'fontSize': '16px'
                    })
                ]),

                # Download button above chart
                html.Div([
                    download_button,
                    download_component
                ], style={
                    'display': 'flex',
                    'justifyContent': 'right',
                    'marginBottom': '10px',
                    'width': '90%',
                    'margin': '0 auto',
                    'paddingRight': '10px',
                    'paddingBottom': '10px'
                }),

                # Chart
                html.Div([
                    dcc.Graph(
                        id='wue-scatter-chart',
                        style={
                            'height': 'calc(100vh - 400px)',
                            'width': '100%'
                        },
                        config={
                            'responsive': True
                        }
                    )
                ], style={
                    'width': '90%',
                    'margin': '0 auto'
                })
            ], style={
                'flex': '1',
                'padding': '30px',
                'minWidth': '0',
                'overflow': 'hidden'
            })
        ], style={
            'display': 'flex',
            'flexDirection': 'row',
            'minHeight': 'calc(100vh - 40px)',
            'backgroundColor': '#f8f9fa'
        })
    ])

    return create_base_layout(content)

    #         wue_filter_manager.create_filter_components(),
    #         dcc.Graph(id='wue-scatter-chart')
    #     ], style={'padding': '20px', 'maxWidth': '1200px', 'margin': 'auto'})
    # ])

