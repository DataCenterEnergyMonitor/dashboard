from dash import html
from components.navbar import create_navbar

def create_about_page():
    return html.Div([
        create_navbar(),
        html.Div([
            html.H1(
                "Data Centers 101",
                style={'fontFamily': 'Roboto', 'fontWeight': '500', 'marginBottom': '30px'}
            ),
            html.P(
                "Coming soon",
                style={
                    'fontFamily': 'Roboto',
                    'marginBottom': '20px',
                    'color': '#404040',
                    'maxWidth': '800px'
                }
            )
        ], style={'padding': '20px', 'maxWidth': '1200px', 'margin': 'auto'})
    ])
