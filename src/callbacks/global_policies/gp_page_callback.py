from dash import Input, Output, State, callback_context, html

# import the tab creation functions
from pages.global_policies.gp_tab1 import create_gp_tab1
from pages.global_policies.gp_tab2 import create_gp_tab2
from pages.global_policies.gp_tab3 import create_gp_tab3
from pages.global_policies.gp_tab4 import create_gp_tab4
from components.bookmark_tabs import get_tab_styles

# Track if callbacks have been registered to prevent duplicates
_gp_callbacks_registered = False

# ID prefix for this page's components
ID_PREFIX = "gp-"


def register_gp_page_callbacks(app, gp_base_df, globalpolicies_df):
    """Registers all callbacks related to the Global Policies page."""
    global _gp_callbacks_registered

    if _gp_callbacks_registered:
        return  # Already registered, skip to prevent duplicates

    _gp_callbacks_registered = True

    @app.callback(
        [
            Output(f"{ID_PREFIX}tabs-content-container", "children"),
            Output(f"{ID_PREFIX}active-tab-store", "data"),
            Output(f"{ID_PREFIX}tab-btn-tab-1", "style"),
            Output(f"{ID_PREFIX}tab-btn-tab-2", "style"),
            Output(f"{ID_PREFIX}tab-btn-tab-3", "style"),
            Output(f"{ID_PREFIX}tab-btn-tab-4", "style"),
        ],
        [
            Input(f"{ID_PREFIX}tab-btn-tab-1", "n_clicks"),
            Input(f"{ID_PREFIX}tab-btn-tab-2", "n_clicks"),
            Input(f"{ID_PREFIX}tab-btn-tab-3", "n_clicks"),
            Input(f"{ID_PREFIX}tab-btn-tab-4", "n_clicks"),
        ],
        [State(f"{ID_PREFIX}active-tab-store", "data")],
        prevent_initial_call=False,
    )
    def render_tab_content(btn1_clicks, btn2_clicks, btn3_clicks, btn4_clicks, current_tab):
        """Dynamically loads and returns the content for the selected tab."""

        # Determine which button was clicked
        ctx = callback_context
        if not ctx.triggered:
            # Initial load - use current_tab or default to tab-1
            active_tab = current_tab or "tab-1"
        else:
            # Get the button ID that was clicked
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            # Extract tab value from button ID (e.g., 'gp-tab-btn-tab-1' -> 'tab-1')
            active_tab = button_id.replace(f"{ID_PREFIX}tab-btn-", "")

        # Render content based on active tab
        if active_tab == "tab-1":
            content = create_gp_tab1(app, globalpolicies_df)
        elif active_tab == "tab-2":
            content = create_gp_tab2(app, globalpolicies_df)
        elif active_tab == "tab-3":
            content = create_gp_tab3(app, globalpolicies_df)
        elif active_tab == "tab-4":
            content = create_gp_tab4(app, gp_base_df)
        else:
            content = html.Div("Select a tab to view the data visualization.")

        # Get consistent tab styles
        active_style, inactive_style = get_tab_styles()

        # Apply styles based on active tab
        style1 = active_style if active_tab == "tab-1" else inactive_style
        style2 = active_style if active_tab == "tab-2" else inactive_style
        style3 = active_style if active_tab == "tab-3" else inactive_style
        style4 = active_style if active_tab == "tab-4" else inactive_style

        return content, active_tab, style1, style2, style3, style4
