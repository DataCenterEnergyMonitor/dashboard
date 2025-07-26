from dash import html
from components.navbar_data_page import create_navbar
from components.footer import create_footer

def create_data_page_layout(content):
    return html.Div(
        style={
            'display': 'flex',
            'flexDirection': 'column',
            'minHeight': '100vh'  # ensure the layout takes at least the full height of the viewport
        },
        children=[
            create_navbar(),
            html.Div(
                content,
                style={'flex': '1'}  # allow the content area to grow and fill space
            ),
            create_footer()
        ]
    ) 