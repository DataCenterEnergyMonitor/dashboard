from dash import html, dcc


def create_rt_tab4():
    """
    Create tab 4 content (Methodology page - static HTML).
    Note: This is tab content, not a full page, so no base_layout wrapper.
    """
    content = html.Div(
        [
            # Back navigation button
            html.Div(
                [
                    dcc.Link(
                        html.Div(
                            [
                                html.I(
                                    className="fas fa-arrow-left",
                                    style={"marginRight": "8px"},
                                ),
                                "Explore Company Reporting Data",
                            ],
                            style={
                                "display": "flex",
                                "alignItems": "center",
                                "padding": "8px 16px",
                                "color": "#6c757d",
                                "textDecoration": "none",
                                "fontSize": "0.9rem",
                                "transition": "all 0.2s ease",
                            },
                        ),
                        href="/reporting",
                        style={"textDecoration": "none"},
                    )
                ],
                style={
                    "position": "fixed",
                    "top": "90px",
                    "left": "120px",
                    "zIndex": "1001",
                    "backgroundColor": "white",
                    "padding": "10px",
                    "borderRadius": "8px",
                },
            ),
            html.Div(
                [
                    html.Iframe(
                        src="assets/static_pages/company_reporting/rt_methodology.html",
                        style={
                            "width": "100vw",
                            "height": "calc(100vh - 170px)",
                            "border": "none",
                            "borderRadius": "0",
                            "backgroundColor": "#ffffff",
                            "position": "relative",
                            "left": "0",
                            "right": "0",
                        },
                    )
                ],
                style={
                    "width": "100vw",
                    "height": "calc(100vh - 120px)",
                    "margin": "0",
                    "padding": "50px 0 0 0",
                    "backgroundColor": "#ffffff",
                    "borderRadius": "0",
                },
            ),
        ],
        style={
            "padding": "0",
            "backgroundColor": "#ffffff",
            "minHeight": "calc(100vh - 100px)",
            "width": "100vw",
            "margin": "0",
            "position": "relative",
        },
    )

    return content
