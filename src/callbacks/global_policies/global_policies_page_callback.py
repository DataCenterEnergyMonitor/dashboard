from dash import Input, Output, State, callback_context, html

# import the tab creation functions
from components.tabs.global_policies.stacked_area_tab import create_stacked_area_tab
from components.tabs.global_policies.heatmap_tab import create_heatmap_tab
from components.tabs.global_policies.choropleth_map_tab import create_choropleth_map_tab

# Track if callbacks have been registered to prevent duplicates
_global_policies_callbacks_registered = False


def register_global_policies_page_callbacks(app, globalpolicies_df):
    """Registers all callbacks related to the Global Policies page."""
    global _global_policies_callbacks_registered

    if _global_policies_callbacks_registered:
        return  # Already registered, skip to prevent duplicates

    _global_policies_callbacks_registered = True

    @app.callback(
        [
            Output("tabs-content-container", "children"),
            Output("active-tab-store", "data"),
            Output("tab-btn-tab-1", "style"),
            Output("tab-btn-tab-2", "style"),
            Output("tab-btn-tab-3", "style"),
        ],
        [
            Input("tab-btn-tab-1", "n_clicks"),
            Input("tab-btn-tab-2", "n_clicks"),
            Input("tab-btn-tab-3", "n_clicks"),
        ],
        [State("active-tab-store", "data")],
        prevent_initial_call=False,
    )
    def render_tab_content(btn1_clicks, btn2_clicks, btn3_clicks, current_tab):
        """Dynamically loads and returns the content for the selected tab."""

        # Determine which button was clicked
        ctx = callback_context
        if not ctx.triggered:
            # Initial load - use current_tab or default to tab-1
            active_tab = current_tab or "tab-1"
        else:
            # Get the button ID that was clicked
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            # Extract tab value from button ID (e.g., 'tab-btn-tab-1' -> 'tab-1')
            active_tab = button_id.replace("tab-btn-", "")

        # Render content based on active tab
        if active_tab == "tab-1":
            content = create_stacked_area_tab(app, globalpolicies_df)
        elif active_tab == "tab-2":
            content = create_heatmap_tab(app, globalpolicies_df)
        elif active_tab == "tab-3":
            content = create_choropleth_map_tab(app, globalpolicies_df)
        else:
            content = html.Div("Select a tab to view the data visualization.")

        # Define styles for active and inactive tabs
        # Match bookmark bar button styles exactly
        active_style = {
            "border-radius": "15px",
            "border": "none",
            "backgroundColor": "rgba(0, 88, 141, 0.9)",
            "font-size": "0.85rem",
            "padding": "5px 20px",
            "text-decoration": "none",
            "color": "#ffffff",
            "display": "inline-block",
        }

        inactive_style = {
            "border": "none",
            "font-size": "0.85rem",
            "padding": "5px 15px",
            "text-decoration": "none",
            "color": "#6c757d",
        }

        # Apply styles based on active tab
        style1 = active_style if active_tab == "tab-1" else inactive_style
        style2 = active_style if active_tab == "tab-2" else inactive_style
        style3 = active_style if active_tab == "tab-3" else inactive_style

        return content, active_tab, style1, style2, style3
