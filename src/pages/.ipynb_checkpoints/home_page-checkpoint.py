from dash import html
from components.navbar import create_navbar

def create_home_page():
    return html.Div([
        create_navbar(),
        html.Div([
            html.H1(
                "Data Center Energy Monitor",
                style={'fontFamily': 'Roboto', 'fontWeight': '500', 'marginBottom': '30px'}
            ),
            html.P(
                "Welcome to the Data Center Analytics Dashboard. "
                "This platform provides comprehensive insights into data center energy reporting metrics.",
                style={
                    'fontFamily': 'Roboto',
                    'marginBottom': '20px',
                    'color': '#404040',
                    'maxWidth': '800px'
                }
            ),
            html.Div([
                html.H2("Explore Trends", style={'marginTop': '2rem'}),
                html.Ul([
                    html.Li(html.A("PUE Trends", href="/pue")),
                    html.Li(html.A("WUE Trends", href="/wue")),
                    html.Li(html.A("About the Project", href="/about")),
                ])
            ])
        ], style={'padding': '20px', 'maxWidth': '1200px', 'margin': 'auto'})
    ])
