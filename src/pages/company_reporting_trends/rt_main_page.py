from dash import dcc, html
from layouts.base_layout import create_base_layout
from components.bookmark_tabs import create_bookmark_tabs


def create_rt_page(app, reporting_df):
    """
    Creates the company reporting trends page layout.
    Filters are inside each tab for flexibility.
    Filter values are synced via rt-filter-store.
    """
    # Extract years from data for default filter values - convert to Python int
    years = sorted([int(y) for y in reporting_df["reported_data_year"].unique()])
    min_year, max_year = int(min(years)), int(max(years))

    # Define tabs configuration - use simple values, prefix is added by component
    tabs_config = [
        {"label": "Reporting Adoption", "value": "tab-1"},
        {"label": "Energy", "value": "tab-2"},
        {"label": "Water", "value": "tab-3"},
        {"label": "PUE", "value": "tab-4"},
        {"label": "WUE", "value": "tab-5"},
    ]

    # Create bookmark-styled tabs component with "rt-" prefix for ID namespacing
    tabs_component = create_bookmark_tabs(
        tabs_config=tabs_config,
        active_tab_id="tab-1",
        data_page_parent="company_reporting_trends",
        id_prefix="rt-",
    )

    # Shared filter store for cross-tab filter synchronization
    # This persists when switching tabs - values synced via callbacks
    filter_store = dcc.Store(
        id="rt-filter-store",
        data={"from_year": min_year, "to_year": max_year, "source": "initial"},
    )

    # Empty div to be populated by the callback
    content_container = html.Div(id="rt-tabs-content-container")

    # Wrap tabs in a sticky container
    # Tabs start after sidebar (320px) since tab content has sidebar
    sticky_tabs = html.Div(
        [tabs_component],
        className="d-none d-lg-block",  # Hide on mobile, show on desktop
        id="rt-tabs-container",
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
            "display": "block",
            "visibility": "visible",
        },
    )

    # Add spacing div to account for fixed tabs
    tabs_spacer = html.Div(style={"height": "80px"})

    content = html.Div([filter_store, sticky_tabs, tabs_spacer, content_container])

    # Return the full layout
    return create_base_layout(content)
