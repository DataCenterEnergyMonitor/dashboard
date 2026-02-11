from dash import dcc, html
from layouts.base_layout import create_base_layout
from components.bookmark_tabs import create_bookmark_tabs


def create_rt_page(app, reporting_df, pue_wue_companies_df):
    """
    Creates the company reporting trends page layout.
    Filters are inside each tab for flexibility.
    Filter values are synced via rt-filter-store.
    """
    # Extract years from data for default filter values - convert to Python int
    years = sorted([int(y) for y in reporting_df["reported_data_year"].unique()])
    rt_min_year, rt_max_year = int(min(years)), int(max(years))

    pw_years = sorted([int(y) for y in pue_wue_companies_df["year"].unique()])
    pw_min_year, pw_max_year = int(min(pw_years)), int(max(pw_years))

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

    # Default values for Clear All (rt_filter_callbacks reads these from store).
    filter_store = dcc.Store(
        id="rt-filter-store",
        data={
            "default_rt_from_year": rt_min_year, #tab 1-3
            "default_rt_to_year": rt_max_year, #tab 1-3
            "default_pw_from_year": pw_min_year, #tab 4-5
            "default_pw_to_year": pw_max_year, #tab 4-5
            "sort_by": "company_name",
            "sort_order": "asc",
            "source": "initial",
            "timestamp": 0,
        },
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
