from dash import html, dcc
from components.filter_manager import FilterManager, FilterConfig
from components.navbar import create_navbar

def create_forecast_page(app, forecast_df):
    print("Forecast DataFrame shape:", forecast_df.shape)
    print("Forecast DataFrame columns:", forecast_df.columns)
    print("Sample data:", forecast_df.head())
    # Define Energy Forecast-specific filters with dependencies
    forecast_filters = [
        FilterConfig(
            id="geographic_scope",
            label="Location",
            column="geographic_scope",
            multi=False,
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
    
    # Initialize forecast-specific filter manager
    forecast_filter_manager = FilterManager(app, "energy", forecast_df, forecast_filters)
    
    return html.Div([
        create_navbar(),
        html.Div([
            html.H1(
                "Energy Forecasts for Data Centers",
                style={'fontFamily': 'Roboto', 'fontWeight': '500', 'marginBottom': '30px', 'fontSize': '32px'}
            ),
            html.Div([
                html.P([
                    "Reported Energy Consumption Trends and Predictions for Data Center",
                    html.Br()
                ], style={
                    'fontFamily': 'Roboto',
                    'marginBottom': '20px',
                    'color': '#404040',
                    'maxWidth': '800px',
                    'fontSize': '16px'
                })
            ]),
            forecast_filter_manager.create_filter_components(),
            dcc.Graph(id='forecast-scatter-chart')
        ], style={'padding': '20px', 'maxWidth': '1200px', 'margin': 'auto'})
    ])

