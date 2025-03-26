from dash import html, dcc

def create_download_button(button_id: str, download_id: str) -> html.Div:
    """
    Create a standardized download button component.
    
    Args:
        button_id (str): ID for the button element
        download_id (str): ID for the download component
    
    Returns:
        html.Div: Download button container with consistent styling
    """
    return html.Div([
        html.Button(
            "Download Data",
            id=button_id,
            style={
                'backgroundColor': '#4CAF50',
                'color': 'white',
                'padding': '8px 16px',
                'border': 'none',
                'borderRadius': '4px',
                'cursor': 'pointer',
                'fontFamily': 'Inter',
                'fontWeight': '500',
                'fontSize': '14px'
            }
        ),
        dcc.Download(id=download_id)
    ], style={
        'display': 'flex',
        'justifyContent': 'right',
        'marginBottom': '10px',
        'width': '90%',
        'margin': '0 auto',
        'paddingRight': '10px',
        'paddingBottom': '10px'
    }) 