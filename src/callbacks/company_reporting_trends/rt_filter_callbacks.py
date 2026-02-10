"""
Filter callbacks for Company Reporting Trends page.

This module handles all filter-related callbacks including:
- Syncing filter values to the shared store (Apply button)
- Clearing filters (Clear All button)
- Resetting filter UI components

The filter store (rt-filter-store) is shared across all tabs and contains:
- from_year, to_year: shared across all tabs
- companies: shared across tabs 2-5
- pw_status: shared across tabs 4-5
- sort_by: sorting option for heatmaps (tabs 2-5)
- sort_order: ascending or descending
- timestamp: for cache busting
"""

import time
import dash
from dash import Input, Output, State, callback_context


# ID prefix for this page's components
ID_PREFIX = "rt-"

# Default pw_status values for tabs 4-5 (all statuses selected by default)
DEFAULT_PW_STATUS = [
    "company not established",
    "company Inactive",
    "no reporting evident",
    "individual data center values only",
    "fleet-wide values only",
    "both fleet-wide and individual data center values",
    "pending",
]

# Default reporting status options for tab 2 (energy heatmap)
DEFAULT_TAB2_REPORTING_STATUS = [
    "No Reporting",
    "Pending",
    "Company Wide Electricity Use",
    "Data Center Fuel Use",
    "Data Center Electricity Use",
]


def register_rt_filter_callbacks(app):
    """Register all filter-related callbacks for the Company Reporting Trends page.

    Args:
        app: Dash app instance
    """

    @app.callback(
        Output(f"{ID_PREFIX}filter-store", "data"),
        [
            Input("apply-filters-btn", "n_clicks"),
            Input("rt-clear-filters-btn", "n_clicks"),
        ],
        [
            State("rt-from-year", "value"),
            State("rt-to-year", "value"),
            State("rt-company-filter", "value"),
            State("pw_reporting_status", "value"),
            State("rt_tab2_reporting_status", "value"),
            State("rt-sort-by", "value"),
            State("rt-sort-order", "value"),
            State(f"{ID_PREFIX}filter-store", "data"),
            State(f"{ID_PREFIX}active-tab-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def sync_filters_to_store(
        apply_clicks,
        clear_clicks,
        from_year,
        to_year,
        companies,
        pw_status,
        tab2_reporting_status,
        sort_by,
        sort_order,
        current_store,
        active_tab,
    ):
        """Sync filter component values to shared store when Apply or Clear is clicked.

        This is the single source of truth for filter state across all tabs.
        """
        ctx = callback_context

        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        timestamp = time.time()

        base = current_store.copy() if current_store else {}

        # Handle clear filters button
        if trigger_id == "rt-clear-filters-btn":
            out = {
                "from_year": None,
                "to_year": None,
                "companies": None,
                "pw_status": DEFAULT_PW_STATUS
                if active_tab in ["tab-4", "tab-5"]
                else None,
                "sort_by": "company_name",
                "sort_order": "asc",
                "source": "clear",
                "timestamp": timestamp,
            }

            # For tab 2, reset status filter to its full default list on Clear.
            # For other tabs, preserve whatever is currently in the store.
            if active_tab == "tab-2":
                out["tab2_reporting_status"] = DEFAULT_TAB2_REPORTING_STATUS
            else:
                out["tab2_reporting_status"] = base.get("tab2_reporting_status")

            return out

        # Handle apply filters button
        # Only overwrite fields that are visible on the current tab; keep rest from store
        # so one Apply applies to all tabs (tab 1 = year only; 2-3 = year + company + sort; 4-5 = all)
        if trigger_id == "apply-filters-btn":
            out = {
                "from_year": int(from_year) if from_year else base.get("from_year"),
                "to_year": int(to_year) if to_year else base.get("to_year"),
                "companies": base.get("companies"),
                "pw_status": base.get("pw_status"),
                "sort_by": base.get("sort_by", "company_name"),
                "sort_order": base.get("sort_order", "asc"),
                "source": "apply",
                "timestamp": timestamp,
            }
            if active_tab in ("tab-2", "tab-3", "tab-4", "tab-5"):
                out["companies"] = (
                    companies if companies is not None else base.get("companies")
                )
                out["sort_by"] = sort_by or base.get("sort_by", "company_name")
                out["sort_order"] = sort_order or base.get("sort_order", "asc")
            if active_tab in ("tab-4", "tab-5"):
                out["pw_status"] = (
                    pw_status if pw_status is not None else base.get("pw_status")
                )

            # Tab-2 specific status filter: only update when we're on tab 2.
            if active_tab == "tab-2":
                out["tab2_reporting_status"] = (
                    tab2_reporting_status
                    if tab2_reporting_status is not None
                    else DEFAULT_TAB2_REPORTING_STATUS
                )
            else:
                out["tab2_reporting_status"] = base.get("tab2_reporting_status")

            return out

        raise dash.exceptions.PreventUpdate

    @app.callback(
        [
            Output("rt-from-year", "value", allow_duplicate=True),
            Output("rt-to-year", "value", allow_duplicate=True),
            Output("rt-company-filter", "value", allow_duplicate=True),
            Output("pw_reporting_status", "value", allow_duplicate=True),
            Output("rt-sort-by", "value", allow_duplicate=True),
            Output("rt-sort-order", "value", allow_duplicate=True),
            Output("rt_tab2_reporting_status", "value", allow_duplicate=True),
        ],
        [Input("rt-clear-filters-btn", "n_clicks")],
        [State(f"{ID_PREFIX}active-tab-store", "data")],
        prevent_initial_call=True,
    )
    def clear_filter_ui_components(clear_clicks, active_tab):
        """Reset filter UI components when Clear All is clicked.

        This callback handles the visual reset of filter components.
        The store update is handled separately by sync_filters_to_store.
        """
        if clear_clicks:
            return (
                None,  # from_year
                None,  # to_year
                None,  # companies
                DEFAULT_PW_STATUS
                if active_tab in ["tab-4", "tab-5"]
                else [],  # pw_status
                "company_name",  # sort_by
                "asc",  # sort_order
                DEFAULT_TAB2_REPORTING_STATUS
                if active_tab == "tab-2"
                else [],  # rt_tab2_reporting_status
            )
        return dash.no_update

    @app.callback(
        [
            Output("rt-sort-by", "value", allow_duplicate=True),
            Output("rt-sort-order", "value", allow_duplicate=True),
            Output("rt-company-filter", "value", allow_duplicate=True),
            Output("pw_reporting_status", "value", allow_duplicate=True),
            Output("rt_tab2_reporting_status", "value", allow_duplicate=True),
        ],
        [Input(f"{ID_PREFIX}active-tab-store", "data")],
        [State(f"{ID_PREFIX}filter-store", "data")],
        prevent_initial_call=True,
    )
    def sync_filter_ui_from_store(active_tab, filter_data):
        """Sync filter UI components from store when switching tabs.

        This ensures filter dropdowns show the correct values when switching
        between tabs, rather than resetting to defaults.
        """
        if not filter_data:
            raise dash.exceptions.PreventUpdate

        sort_by = filter_data.get("sort_by", "company_name")
        sort_order = filter_data.get("sort_order", "asc")
        companies = filter_data.get("companies")
        pw_status = filter_data.get("pw_status")
        tab2_status = filter_data.get("tab2_reporting_status")

        # For tabs 4-5, ensure pw_status has default if not set
        if active_tab in ["tab-4", "tab-5"] and not pw_status:
            pw_status = DEFAULT_PW_STATUS

        # For tab-2, ensure reporting status has default if not set
        if active_tab == "tab-2":
            if not tab2_status:
                tab2_status = DEFAULT_TAB2_REPORTING_STATUS
        else:
            # On other tabs keep it empty/hidden
            if tab2_status is None:
                tab2_status = []

        return sort_by, sort_order, companies, pw_status, tab2_status
