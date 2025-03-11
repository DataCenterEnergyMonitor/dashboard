from dash import html, dcc
import dash_bootstrap_components as dbc
from components.filter_manager import FilterManager, FilterConfig
from layouts.base_layout import create_base_layout
from components.filter_panel import create_filter_panel

def create_reporting_page(app, reporting_df):
    """Create the reporting page with year range filter"""
    # Define reporting trends filters
    reporting_filters = [
        FilterConfig(
            id="year_range",
            label="Year Range",
            column="reported_data_year",
            type="year_range",
            default_value={'from': min(reporting_df['reported_data_year']), 
                         'to': max(reporting_df['reported_data_year'])}
        )
    ]
    
    # Create filter manager
    reporting_filter_manager = FilterManager(app, "reporting", reporting_df, reporting_filters)
    
    # Get filter components
    filter_components = reporting_filter_manager.create_filter_components()
    
    # Extract download button and component
    download_button = html.Button(
        "Download Data",
        id="reporting-download-button",
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
    download_component = dcc.Download(id="reporting-download-data")

    # Main content
    content = html.Div([
        # Main content container with flex layout
        html.Div([
            # Left side - Filter Panel (empty but maintains consistent layout)
            html.Div([
                # Filter Panel Header with Icon
                html.Div([
                    html.I(className="fas fa-filter", 
                          style={
                              'fontSize': '24px', 
                              'color': '#4CAF50', 
                              'marginBottom': '20px'})
                ], style={
                    'display': 'flex', 
                    'justifyContent': 'flex-start', 
                    'width': '100%'}),
                
                # Filter Components (empty in this case)
                filter_components
            ], id='filter-panel', style={
                'width': '260px',
                'backgroundColor': 'white',
                'padding': '20px',
                'boxShadow': 'none',
                'height': 'calc(100vh - 76px)',
                'overflowY': 'auto',
                'position': 'relative'
            }),
            
            # Right side - Main Content
            html.Div([
                html.H1(
                    "Trends in Data Center Energy Reporting Over Time",
                    style={
                        'fontFamily': 'Roboto, sans-serif', 
                        'fontWeight': '500', 
                        'marginBottom': '30px',
                        'fontSize': '32px',
                        'paddingTop': '0px'
                        }
                ),
                
                # Download button container
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
                
                # Chart container
                html.Div([
                    dcc.Graph(
                        id='reporting-bar-chart',
                        style={
                            'height': 'calc(100vh - 400px)',
                            'width': '100%'},
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