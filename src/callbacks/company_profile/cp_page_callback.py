from dash import Input, Output, State, callback_context, html

from pages.company_profile.cp_tab1 import create_cp_tab1
from pages.company_profile.cp_tab2 import create_cp_tab2
from pages.company_profile.cp_tab3 import create_cp_tab3
from pages.company_profile.cp_tab4 import create_cp_tab4
from components.bookmark_tabs import get_tab_styles

# Track if callbacks have been registered to prevent duplicates
_cp_page_callbacks_registered = False

# ID prefix for this page's components
ID_PREFIX = "cp-"


def register_cp_page_callbacks(app, companies, default_company, energy_use_df):
    """Registers the tab-switching callback for the Company Profile page.

    Args:
        app: Dash app instance
        companies: sorted list of company names for the dropdown
        default_company: initially selected company
    """
    global _cp_page_callbacks_registered

    if _cp_page_callbacks_registered:
        return

    _cp_page_callbacks_registered = True

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
        [
            State(f"{ID_PREFIX}active-tab-store", "data"),
            State(f"{ID_PREFIX}filter-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def render_tab_content(
        btn1_clicks, btn2_clicks, btn3_clicks, btn4_clicks,
        current_tab, filter_data,
    ):
        """Dynamically loads and returns the content for the selected tab."""

        ctx = callback_context
        if not ctx.triggered:
            active_tab = current_tab or "tab-1"
        else:
            button_id = ctx.triggered[0]["prop_id"].split(".")[0]
            active_tab = button_id.replace(f"{ID_PREFIX}tab-btn-", "")

        # Read current company from the filter store so the sidebar dropdown
        # shows the right value when a tab is (re-)rendered.
        selected_company = (
            filter_data.get("company") if filter_data else default_company
        )

        if active_tab == "tab-1":
            content = create_cp_tab1(companies, selected_company)
        elif active_tab == "tab-2":
            content = create_cp_tab2(companies, selected_company)
        elif active_tab == "tab-3":
            content = create_cp_tab3(energy_use_df, selected_company)
        elif active_tab == "tab-4":
            content = create_cp_tab4(companies, selected_company)
        else:
            content = html.Div("Select a tab.")

        active_style, inactive_style = get_tab_styles()

        style1 = active_style if active_tab == "tab-1" else inactive_style
        style2 = active_style if active_tab == "tab-2" else inactive_style
        style3 = active_style if active_tab == "tab-3" else inactive_style
        style4 = active_style if active_tab == "tab-4" else inactive_style

        return content, active_tab, style1, style2, style3, style4
