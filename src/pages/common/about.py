from dash import html
from layouts.base_layout import create_base_layout


def create_about_page():
    content = html.H4(
        "Coming soon...",
        style={
            "width": "50%",  # Define a width
            "margin": "0 auto",  # Center horizontally
            "textAlign": "center",  # Center text within the block
            "paddingTop": "50px",
        },
    )

    return create_base_layout(content)  # Use the base layout
