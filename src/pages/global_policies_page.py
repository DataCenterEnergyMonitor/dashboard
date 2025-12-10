from dash import html
from layouts.base_layout import create_base_layout
from components.bookmark_tabs import create_bookmark_tabs


def create_global_policies_page(app, globalpolicies_df):
    """
    Creates the main policies page layout
    """

    # Define tabs configuration
    tabs_config = [
        {"label": "Cumulative Trends", "value": "tab-1"},
        {"label": "Policy Matrix", "value": "tab-2"},
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

    content = html.Div([tabs_component, content_container])

    # Note: Callbacks are registered in app.py to avoid validation issues
    # register_global_policies_page_callbacks(app, globalpolicies_df)
    # register_global_policies_area_callbacks()

    # Return the full layout
    return create_base_layout(content)
