from dash import html, dcc
import dash_bootstrap_components as dbc


def create_download_button(button_id: str, download_id: str) -> html.Div:
    """Create a download button matching the design from the image."""
    button_style = {
        "backgroundColor": "#2E8B57",  # Lighter green for normal state
        "color": "white",
        "border": "none",
        "borderRadius": "4px",
        "padding": "8px 16px",
        "fontSize": "14px",
        "fontWeight": "500",
        "display": "inline-flex",
        "alignItems": "center",
        "gap": "8px",
        "cursor": "pointer",
        "transition": "background-color 0.2s",
    }

    return html.Div(
        [
            html.Button(
                [html.I(className="fas fa-download me-2"), "Download (.xlsx)"],
                id=button_id,
                style=button_style,
                className="download-button",
            ),
            dcc.Download(id=download_id),
        ],
        style={
            "display": "flex",
            "justifyContent": "flex-end",  # Align button to the right
            "width": "100%",
            "paddingRight": "20px",
            "marginTop": "10px",
            "marginBottom": "20px",
        },
    )
