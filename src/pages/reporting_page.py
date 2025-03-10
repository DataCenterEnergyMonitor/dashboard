from dash import html, dcc
import dash_bootstrap_components as dbc
from components.filter_manager import FilterManager, FilterConfig
from layouts.base_layout import create_base_layout
from components.filter_panel import create_filter_panel

def create_reporting_page(app, reporting_df):
    years = sorted(reporting_df['reported_data_year'].unique())
    
    # Define reporting trends filters with dependencies
    reporting_filters = [
        FilterConfig(
            id="reporting_scope",
            label="Reporting Scope",
            column="reporting_scope",
            multi=False,
            default_value=reporting_df['reporting_scope'].iloc[0],
            show_all=True,
            depends_on=None
        ),
        FilterConfig(
            id="reported_data_year",
            label="Year Range",
            column="reported_data_year",
            multi=False,
            default_value=None,
            show_all=False,
            depends_on=None,
            custom_component=dcc.DatePickerRange(
                min_date_allowed=f"{int(min(years))}-01-01",
                max_date_allowed=f"{int(max(years))}-12-31",
                start_date=f"{int(min(years))}-01-01",
                end_date=f"{int(max(years))}-12-31",
                display_format='YYYY',  # Only show year
                calendar_orientation='vertical',
                show_outside_days=False,
                month_format='YYYY',  # Year-only in the calendar header
                style={
                    'zIndex': 1000,
                    'fontFamily': 'Roboto, sans-serif',
                    'fontSize': '14px',
                    'width': '100%'
                }
            )
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
            # Left side - Filter Panel
            html.Div([
                # Filter icon
                html.I(className="fas fa-filter", style={
                    'color': '#4CAF50',
                    'fontSize': '24px',
                    'marginBottom': '20px',
                    'marginLeft': '10px'
                }),
                create_filter_panel(filter_components)
            ], style={
                'width': '260px',
                'backgroundColor': 'white',
                'padding': '20px',
                'boxShadow': '2px 0 5px rgba(0,0,0,0.1)',
                'height': 'calc(100vh - 60px)',
                'position': 'fixed',
                'left': 0,
                'top': '60px',
                'zIndex': 1000
            }),
            
            # Right side - Main Content
            html.Div([
                html.H1(
                    "Trends in Data Center Energy Reporting Over Time",
                    style={
                        'fontFamily': 'Roboto, sans-serif',
                        'fontWeight': '500',
                        'marginBottom': '20px',
                        'fontSize': '32px'
                    }
                ),
                
                # Download button container
                html.Div([
                    download_button,
                    download_component
                ], style={
                    'display': 'flex',
                    'justifyContent': 'right',
                    'marginBottom': '20px'
                }),
                
                # Chart container
                html.Div([
                    dcc.Graph(
                        id='reporting-bar-chart',
                        style={'height': 'calc(100vh - 400px)'},
                        config={'responsive': True}
                    )
                ])
            ], style={
                'flex': '1',
                'padding': '30px',
                'marginLeft': '260px'
            })
        ], style={
            'display': 'flex',
            'minHeight': 'calc(100vh - 60px)',
            'backgroundColor': '#f8f9fa'
        })
    ])

    # Wrap the content in the base layout
    return create_base_layout(content)