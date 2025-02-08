from dash import html

def create_navbar():
    return html.Nav(
        className="navbar",
        children=[
            html.Div(
                className="navbar-content",
                children=[
                    html.A("Home", href="/", className="nav-link"),
                    html.A("PUE Trends", href="/pue", className="nav-link"),
                    html.A("WUE Trends", href="/wue", className="nav-link"),
                    html.A("About", href="/about", className="nav-link"),
                ]
            )
        ],
        style={
            'padding': '1rem',
            'backgroundColor': '#f8f9fa',
            'marginBottom': '2rem'
        }
    )
