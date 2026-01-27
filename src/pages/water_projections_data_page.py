from dash import html, dcc
from layouts.base_layout import create_base_layout


def create_water_projections_data_page():
    content = html.Div([
        # Back navigation button
        html.Div([
            dcc.Link(
                html.Div([
                    html.I(className="fas fa-arrow-left", style={"marginRight": "8px"}),
                    "Explore Water Estimates And Projections Data"
                ], style={
                    "display": "flex",
                    "alignItems": "center",
                    "padding": "8px 16px",
                    "color": "#6c757d",
                    "textDecoration": "none",
                    "fontSize": "0.9rem",
                    "transition": "all 0.2s ease"
                }),
                href="/water-projections",
                style={"textDecoration": "none"}
            )
        ], style={
            "position": "fixed",
            "top": "90px",
            "left": "120px",
            "zIndex": "1001",
            "backgroundColor": "white",
            "padding": "10px",
            "borderRadius": "8px",
        }),
        html.Div([
            html.Iframe(
                src="assets/static_pages/water_projections/water_projections_data.html",
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