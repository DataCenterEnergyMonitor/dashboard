from dash import html, dcc
import dash_bootstrap_components as dbc
from components.year_range import create_year_range_component
from components.download_button import create_download_button
from layouts.base_layout import create_base_layout
# from callbacks.reporting_callbacks import create_reporting_callback

def create_reporting_page(app, reporting_df, data_dict, chart_configs):
    """Create the reporting page with year range filter"""
    years = sorted(reporting_df['reported_data_year'].unique())
    min_year, max_year = min(years), max(years)
    
    # Create year range filter using the component
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
                className="page-title"
            ),
            
            html.Div([
                # Download button above charts
                create_download_button(
                    button_id="btn-download-reporting-data",
                    download_id="download-reporting-data"
                ),
                
                # Bar Chart
                dcc.Graph(
                    id='reporting-bar-chart',
                    style={'height': '500px', 'marginBottom': '20px'}
                ),
                
                # Timeline Chart
                dcc.Graph(
                    id='timeline-bar-chart',
                    style={'height': '600px'}
                )
            ], style={
                'width': '90%',
                'margin': '0 auto'
            })
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