from dash import html, dcc
from layouts.base_layout import create_base_layout


def create_pue_methodology_page():
    content = html.Div([
        # # Back navigation button
        # html.Div([
        #     dcc.Link(
        #         html.Div([
        #             html.I(className="fas fa-chart-bar", style={"marginRight": "8px"}),
        #             "Explore PUE/WUE Data"
        #         ], style={
        #             "display": "flex",
        #             "alignItems": "center",
        #             "padding": "8px 16px",
        #             "backgroundColor": "#f8f9fa",
        #             "border": "1px solid #e9ecef",
        #             "borderRadius": "6px",
        #             "color": "#495057",
        #             "textDecoration": "none",
        #             "fontSize": "0.9rem",
        #             "fontWeight": "500",
        #             "transition": "all 0.2s ease"
        #         }),
        #         href="/pue_wue",  # Update with your actual PUE page route
        #         style={"textDecoration": "none"}
        #     )
        # ], style={
        #     "position": "fixed",
        #     "top": "120px",
        #     "left": "155px",
        #     "zIndex": "1001",
        #     "backgroundColor": "white",
        #     "padding": "10px",
        #     "borderRadius": "8px",
        # }),
        html.Div([
            html.Iframe(
                src="assets/static_pages/pue_wue/pue_methodology.html",
                style={
                    #"width": "100%",
                    "width": "100vw",
                    "height": "calc(100vh - 120px)",
                    "border": "none",
                    "borderRadius": "0",
                    "backgroundColor": "#ffffff",
                    "position": "relative",
                    "left": "0",
                    "right": "0"
                }
            )
        ], style={
            #"width": "100%",
            "width": "100vw",
            "height": "calc(100vh - 120px)",
            "margin": "0",
            "padding": "0",
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