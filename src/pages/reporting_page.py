from dash import html, dcc
from components.year_range import create_year_range_component
from layouts.base_layout import create_base_layout

def create_reporting_page(app, reporting_df):
    """Create the reporting page with year range filter"""
    years = sorted(reporting_df['reported_data_year'].unique())
    min_year, max_year = min(years), max(years)
    
    # Create year range filter component
    year_range_filter = create_year_range_component(
        base_id="reporting",
        years=years,
        default_from=min_year,
        default_to=max_year
    )

    content = html.Div([
        # Left side - Filter Panel
        html.Div([
            year_range_filter
        ], style={
            'width': '260px',
            'padding': '20px',
            'backgroundColor': '#f8f9fa',
            'borderRight': '1px solid #dee2e6'
        }),
        
        # Right side - Charts
        html.Div([
            html.H1(
                "Trends in Data Center Energy Reporting Over Time",
                style={
                    'fontFamily': 'Roboto, sans-serif',
                    'marginBottom': '20px',
                    'color': '#2c3e50'
                }
            ),
            
            # Bar Chart
            dcc.Graph(
                id='reporting-bar-chart',
                style={'height': '500px', 'marginBottom': '20px'}
            ),
            
            # Timeline Chart
            dcc.Graph(
                id='timeline-chart',
                style={'height': '600px'}
            )
        ], style={
            'flex': '1',
            'padding': '20px',
            'backgroundColor': '#ffffff'
        })
    ], style={
        'display': 'flex',
        'minHeight': '100vh',
        'backgroundColor': '#ffffff'
    })

    return create_base_layout(content)