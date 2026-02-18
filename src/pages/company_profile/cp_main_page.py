from dash import dcc, html
from layouts.base_layout import create_base_layout
from components.bookmark_tabs import create_bookmark_tabs

# ID prefix for this page's components
ID_PREFIX = "cp-"


def create_cp_page(app, company_profile_df, energy_use_df):
    """
    Creates the company profile page layout with four tabs.
    Company filter lives in the left sidebar inside each tab and is shared
    across all tabs via cp-filter-store.
    """
    # Extract companies list for the shared dropdown
    companies = sorted(energy_use_df["company_name"].unique())
    default_company = companies[0] if companies else None

    # Define tabs configuration — short labels matching the RT page style
    tabs_config = [
        {"label": "Reporting Profile", "value": "tab-1"},
        {"label": "Energy Trends", "value": "tab-2"},
        {"label": "Energy Comparison", "value": "tab-3"},
        {"label": "Company Overview", "value": "tab-4"},
    ]

    # Create bookmark-styled tabs component with "cp-" prefix for ID namespacing
    tabs_component = create_bookmark_tabs(
        tabs_config=tabs_config,
        active_tab_id="tab-1",
        data_page_parent=None,
        id_prefix=ID_PREFIX,
    )

    # Shared filter store: company selection persists across tabs
    filter_store = dcc.Store(
        id=f"{ID_PREFIX}filter-store",
        data={
            "company": default_company,
            "source": "initial",
        },
    )

    # Empty div to be populated by the tab-switching callback
    content_container = html.Div(id=f"{ID_PREFIX}tabs-content-container")

    # Wrap tabs in a sticky container
    # Tabs start after sidebar (320px) since each tab has its own sidebar
    sticky_tabs = html.Div(
        [tabs_component],
        className="d-none d-lg-block",  # Hide on mobile, show on desktop
        id=f"{ID_PREFIX}tabs-container",
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

    return create_base_layout(content)
