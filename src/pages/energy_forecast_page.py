from dash import html, dcc
from components.filter_manager import FilterManager, FilterConfig
from components.navbar import create_navbar
from components.filter_panel import create_filter_panel
from components.download_button import create_download_button
from layouts.base_layout import create_base_layout

def create_forecast_page(app, forecast_df):
    print("\nCreating forecast page")
    print("Forecast data shape:", forecast_df.shape)
    
    # Define Energy Forecast-specific filters with dependencies
    forecast_filters = [
        FilterConfig(
            id="geographic_scope",
            label="Location",
            column="geographic_scope",
            multi=True,
            default_value="Global",
            show_all=False,
            depends_on=None
        ),
        FilterConfig(
            id="peer_reviewed_",
            label="Peer Reviewed?",
            column="peer_reviewed_",
            multi=True,
            default_value="Yes",
            show_all=True,
            depends_on=None
        ),
        FilterConfig(
            id="author_type_s_",
            label="Author Type",
            column="author_type_s_",
            multi=True,
            default_value="Academic", 
            show_all=True,
            depends_on=None
        ) 
    ]
    
    print("Filter configurations:", [f.id for f in forecast_filters])
    
    # Initialize forecast-specific filter manager
    forecast_filter_manager = FilterManager(app, "forecast", forecast_df, forecast_filters)
    filter_components = forecast_filter_manager.create_filter_components()
    
    print("Created filter components")
    
    content = html.Div([
        # Main content container
        html.Div([
            # Left side - Filter Panel
            html.Div([
                create_filter_panel(filter_components)
            ], style={
                'width': '260px',
                'flexShrink': '0',
                'backgroundColor': '#f8f9fa',
                'borderRight': '1px solid #dee2e6'
            }),
            
            # Right side - Main Content
            html.Div([
                html.H1(
                    "Energy Forecasts for Data Centers",
                    className="page-title"
                ),
                html.Div([
                    html.P([
                        "Reported Energy Consumption Trends and Predictions for Data Center",
                    ], className="body-text")
                ]),
                
                # Download button above chart
                html.Div([
                    create_download_button(
                        button_id="btn-download-forecast-data",
                        download_id="download-forecast-data"
                    )
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
                        id='forecast-scatter-chart',
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

