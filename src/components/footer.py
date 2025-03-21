from dash import html

def create_footer():
    return html.Footer(
        [
            html.Div(
                [
                    html.Div(
                        "Copyright © 2025 The Regents of the University of California. All Rights Reserved.",
                        className="text-center text-muted me-2"
                    ),
                    html.A("Terms of Use", href="https://www.ucsb.edu/terms-of-use", className="text-muted", target="_blank")
                ],
                className="d-flex justify-content-center"
            ),
            html.Div(
                [
                    #html.A("Privacy Policy", href="/privacy", className="me-2"),
                ],
                className="text-center"
            )
        ],
        className="footer mt-auto py-3 bg-light"
    )