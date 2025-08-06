from dash import html
from layouts.base_layout import create_base_layout


def create_pue_wue_methodology_page():
    content = html.Div([
        html.Div([
            html.Iframe(
                src="assets/static_pages/pue_wue/pue_wue_methodology.html",
                style={
                    "width": "100%",
                    "height": "calc(100vh - 120px)",
                    "border": "none",
                    "borderRadius": "0",
                    "backgroundColor": "#ffffff"
                }
            )
        ], style={
            "width": "100%",
            "height": "calc(100vh - 120px)",
            "margin": "0 auto",
            "padding": "0 20px",
            "backgroundColor": "#ffffff", #"#f8f9fa",
            "borderRadius": "8px"
        })
    ], style={
        "padding": "20px 0",
        "backgroundColor": "#ffffff", #"#f8f9fa",
        "minHeight": "calc(100vh - 100px)"
    })

    return create_base_layout(content)