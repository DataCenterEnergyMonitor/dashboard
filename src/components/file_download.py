from dash import html, dcc


def create_chart_download_button(chart_id: str, tooltip_text: str = "Download data as Excel"):
    """
    Create a simple download button for chart data.
    
    Args:
        chart_id (str): Unique identifier for the chart
        tooltip_text (str): Tooltip text for the button
    
    Returns:
        html.Div: Download button component
    """
    return html.Div([
        html.Button(
            html.I(className="fa-solid fa-download"),
            id=f"download-btn-{chart_id}",
            className="btn btn-outline-secondary btn-sm",
            style={
                "border": "none",
                "backgroundColor": "transparent", 
                "color": "#6c757d",
                "padding": "6px 8px",
                "borderRadius": "4px",
                "transition": "all 0.2s ease",
                "fontSize": "14px"
            },
            title=tooltip_text
        ),
        dcc.Download(id=f"download-{chart_id}")
    ], style={"display": "inline-block", "marginLeft": "8px"})