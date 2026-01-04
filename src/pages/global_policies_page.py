from dash import html
from layouts.base_layout import create_base_layout
from components.bookmark_tabs import create_bookmark_tabs


def create_gp_page(app, globalpolicies_df):
    """
    Creates the main policies page layout
    """

    # Define tabs configuration
    tabs_config = [
        {"label": "Cumulative Trends", "value": "tab-1"},
        {"label": "Jurisdictional Distribution", "value": "tab-2"},
        {"label": "Geographic Distribution", "value": "tab-3"},
    ]

    # Create bookmark-styled tabs component
    tabs_component = create_bookmark_tabs(
        tabs_config=tabs_config,
        active_tab_id="tab-1",
        data_page_parent="global_policies",
    )

    # This empty div will be populated by the callback
    content_container = html.Div(id="tabs-content-container")

    # Wrap tabs in a sticky container (similar to pue_wue_page)
    # Tabs start after sidebar (320px) since tab content has sidebar
    sticky_tabs = html.Div(
        [tabs_component],
        className="d-none d-lg-block",  # Hide on mobile, show on desktop
        id="global-policies-tabs-container",  # Add ID for debugging
        style={
            "position": "fixed",
            "top": "100px",  # Below navbar
            "left": "320px",  # Start after sidebar (matches tab content)
            "right": "0",
            "zIndex": "1001",  # Higher than tab content (1000)
            "backgroundColor": "white",
            "padding": "8px 20px",
            "height": "auto",
            "minHeight": "60px",
            "borderBottom": "1px solid #dee2e6",
            "display": "block",  # Ensure it's always visible
            "visibility": "visible",  # Ensure it's always visible
        },
    )

    # Add spacing div to account for fixed tabs
    tabs_spacer = html.Div(style={"height": "80px"})

    content = html.Div([sticky_tabs, tabs_spacer, content_container])

    # Return the full layout
    return create_base_layout(content)
