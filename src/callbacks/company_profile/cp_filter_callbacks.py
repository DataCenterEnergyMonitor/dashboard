"""
Filter callbacks for the Company Profile page.

Handles:
- Syncing filter values to the shared store (Apply Filters button)
- Clearing filters (Clear All button)
- Resetting filter UI components on Clear

The filter store (cp-filter-store) is shared across all tabs and contains:
- company: selected company (tabs 1-4)
- year: reporting year (tab 3)
- benchmark_companies: companies to compare (tab 3)
- default_company, default_year: reset targets for Clear All
"""

import dash
from dash import Input, Output, State, callback_context

ID_PREFIX = "cp-"


def register_cp_filter_callbacks(app):
    """Register filter-sync callbacks for the Company Profile page."""

    @app.callback(
        Output(f"{ID_PREFIX}filter-store", "data"),
        [
            Input(f"{ID_PREFIX}apply-filters-btn", "n_clicks"),
            Input(f"{ID_PREFIX}clear-filters-btn", "n_clicks"),
        ],
        [
            State(f"{ID_PREFIX}company-dropdown", "value"),
            State(f"{ID_PREFIX}benchmark-companies-dropdown", "value"),
            State(f"{ID_PREFIX}year-dropdown", "value"),
            State(f"{ID_PREFIX}filter-store", "data"),
            State(f"{ID_PREFIX}active-tab-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def sync_cp_filters_to_store(
        apply_clicks, clear_clicks,
        company, benchmark_companies, year,
        current_store, active_tab,
    ):
        """Sync filter component values to the shared store on Apply or Clear."""
        ctx = callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        base = current_store.copy() if current_store else {}

        if trigger_id == f"{ID_PREFIX}clear-filters-btn":
            return {
                "company": base.get("default_company"),
                "year": base.get("default_year"),
                "benchmark_companies": [],
                "default_company": base.get("default_company"),
                "default_year": base.get("default_year"),
                "source": "clear",
            }

        if trigger_id == f"{ID_PREFIX}apply-filters-btn":
            return {
                "company": company or base.get("company"),
                "year": int(year) if year else base.get("year"),
                "benchmark_companies": benchmark_companies
                if benchmark_companies
                else [],
                "default_company": base.get("default_company"),
                "default_year": base.get("default_year"),
                "source": "apply",
            }

        raise dash.exceptions.PreventUpdate

    @app.callback(
        [
            Output(
                f"{ID_PREFIX}company-dropdown", "value", allow_duplicate=True
            ),
            Output(
                f"{ID_PREFIX}benchmark-companies-dropdown",
                "value",
                allow_duplicate=True,
            ),
            Output(
                f"{ID_PREFIX}year-dropdown", "value", allow_duplicate=True
            ),
        ],
        Input(f"{ID_PREFIX}clear-filters-btn", "n_clicks"),
        State(f"{ID_PREFIX}filter-store", "data"),
        prevent_initial_call=True,
    )
    def clear_cp_filter_ui(clear_clicks, current_store):
        """Reset filter UI dropdowns when Clear All is clicked."""
        if not clear_clicks:
            return dash.no_update
        base = current_store or {}
        return (
            base.get("default_company"),
            [],
            base.get("default_year"),
        )
