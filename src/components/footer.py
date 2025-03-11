from dash import html

def create_footer():
    return html.Footer(
        [
            html.Div(
                "© 2024 Data Center Energy Monitor. All rights reserved.",
                className="text-center text-muted"
            ),
            html.Div(
                [
                    html.A("Privacy Policy", href="/privacy", className="me-2"),
                    html.A("Terms of Service", href="/terms")
                ],
                className="text-center"
            )
        ],
        className="footer mt-auto py-3 bg-light"  # Add your desired classes for styling
    )