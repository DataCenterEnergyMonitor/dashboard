from dash import html, dcc
from components.filter_manager import FilterManager, FilterConfig
from layouts.base_layout import create_base_layout

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
    
    # Create filter manager and get filter components
    reporting_filter_manager = FilterManager(app, "reporting", reporting_df, reporting_filters)
    filter_components = reporting_filter_manager.create_filter_components()

    content = html.Div([
        # Left side - Filter Panel
        html.Div([
            html.I(className="fas fa-filter", style={'fontSize': '24px', 'color': '#4CAF50'}),
            filter_components
        ], style={'width': '260px', 'padding': '20px', 'backgroundColor': 'white'}),
        
        # Right side - Charts
        html.Div([
            html.H1("Trends in Data Center Energy Reporting Over Time"),
            
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
        ], style={'flex': '1', 'padding': '20px', 'backgroundColor': '#f8f9fa'})
    ], style={'display': 'flex', 'minHeight': '100vh'})

    return create_base_layout(content)