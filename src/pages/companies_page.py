from dash import html, dcc
from layouts.base_layout import create_base_layout


def create_companies_page():
    content = html.Div([
        html.Div([
            html.Iframe(
                src="assets/static_pages/companies/companies.html",
                style={
                    "width": "100vw",
                    "height": "calc(100vh - 170px)",
                    "border": "none",
                    "borderRadius": "0",
                    "backgroundColor": "#ffffff",
                    "position": "relative",
                    "left": "0",
                    "right": "0"
                }
            )
        ], style={
            "width": "100vw",
            "height": "calc(100vh - 120px)",
            "margin": "0",
            "padding": "50px 0 0 0",
            "backgroundColor": "#ffffff",
            "borderRadius": "0",

        })
    ], style={
        "padding": "0",
        "backgroundColor": "#ffffff",
        "minHeight": "calc(100vh - 100px)",
        "width": "100vw",
        "margin": "0",
        "position": "relative"
    })

    return create_base_layout(content)