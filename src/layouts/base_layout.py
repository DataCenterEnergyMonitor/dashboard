from dash import html
import dash_bootstrap_components as dbc
from components.navbar import create_navbar
from components.footer import create_footer

def create_base_layout(content):
    return html.Div(
        style={
            'display': 'flex',
            'flexDirection': 'column',
            'minHeight': '100vh'  # ensure the layout takes at least the full height of the viewport
        },
        children=[
            dbc.Navbar([
            create_navbar(),
            ], 
            sticky="top", 
            color="primary", 
            dark=True,
            style={
                # "zIndex": "1030",
                # "height": "90px",
                # "alignItems": "center",
                # "padding": "0 20px",
                # "display": "flex"
            }),
            html.Div(
                content,
                style={'flex': '1'}  # allow the content area to grow and fill space
            ),
            create_footer()
        ]
    ) 