import dash_bootstrap_components as dbc
from dash import html, dcc

def create_bookmark_bar(sections, subnav_items=None):
    """Create bookmark navigation bar for data-viz pages"""
    
    bookmark_buttons = []
    for section in sections:
        button = dbc.Button(
            section['title'],
            href=f"#{section['id']}-section",
            color="outline-primary",
            size="sm",
            className="me-2 mb-2 bookmark-btn",
            external_link=True,
            style={
                "border": "none",
                "font-size": "0.85rem",
                "padding": "5px 15px",
                "text-decoration": "none",
                "color": "#6c757d" 
            }
        )
        bookmark_buttons.append(button)
    
    subnav_buttons = []
    if subnav_items:
        for subnav_item in subnav_items:
            # Check if it's a page route or anchor link
            if 'href' in subnav_item:
                href = subnav_item['href']
            else:
                href = f"#{subnav_item['id']}-subnav_item"

            subnav_button = dcc.Link(
                subnav_item['title'],
                href=href,
                className="me-2 mb-2 bookmark-btn",
                style={
                    "border-radius": "15px",
                    "border": "1px solid #6c757d",
                    "backgroundColor": "rgba(0, 88, 141, 0.9)",
                    "font-size": "0.85rem",
                    "padding": "5px 20px",
                    "text-decoration": "none",
                    "color": "#ffffff",
                    "display": "inline-block"
                }
            )
            subnav_buttons.append(subnav_button)
    
    return html.Div([
        html.Div([
            # Left side - bookmark buttons (aligned with chart start)
            html.Div(bookmark_buttons, 
                    className="d-flex flex-wrap",
                    style={"justify-content": "flex-start"}),  # Left align
            
            # Right side - subnav buttons 
            html.Div(subnav_buttons, 
                    className="d-flex flex-wrap",
                    style={"justify-content": "flex-end", "margin-right": "50px"})      # Right align
                    
        ], className="d-flex justify-content-between align-items-center w-100"),  # Space between
    ], className="bookmark-navigation bookmark-bar"
    )