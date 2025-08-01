import dash_bootstrap_components as dbc
from dash import html

def create_bookmark_bar(sections):
    """Create bookmark navigation bar for data-viz pages"""
    
    sections = sections
    
    buttons = []
    for section in sections:
        button = dbc.Button(
            [
                section['title']
            ],
            href=f"#{section['id']}-section",
            color="outline-primary",
            size="sm",
            className="me-2 mb-2 bookmark-btn",
            external_link=True,
            style={
                #"border-radius": "20px",
                #"border": "1px solid #6c757d",
                "border": "none",
                "font-size": "0.85rem",
                "padding": "5px 15px",
                "text-decoration": "none",
                "color": "#6c757d" 
            }
        )
        buttons.append(button)
    
    return html.Div([
        #html.Hr(style={"margin": "10px 0"}),
        html.Div([
            html.Div(buttons, className="d-flex flex-wrap")
        ], className="d-flex align-items-center flex-wrap"),
        html.Hr(style={"margin": "10px 0"})
    ], className="bookmark-navigation bookmark-bar", style={
        #"background-color": "#f8f9fa",
        #"padding": "15px",
        "border-radius": "8px",
        "margin": "10px 0",
        #"box-shadow": "0 2px 4px rgba(0,0,0,0.1)"
    })