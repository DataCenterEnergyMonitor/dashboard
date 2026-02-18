"""
Filter callbacks for the Company Profile page.

Handles syncing the company dropdown value into the shared filter store
(cp-filter-store) so that every tab can read the current selection.
"""

from dash import Input, Output, State

# ID prefix for this page's components
ID_PREFIX = "cp-"


def register_cp_filter_callbacks(app):
    """Register filter-sync callbacks for the Company Profile page."""

    @app.callback(
        Output(f"{ID_PREFIX}filter-store", "data"),
        Input(f"{ID_PREFIX}company-dropdown", "value"),
        State(f"{ID_PREFIX}filter-store", "data"),
        prevent_initial_call=False,
    )
    def sync_company_to_store(company, current_store):
        """Update the filter store when the company dropdown changes."""
        store = current_store or {}
        store["company"] = company
        store["source"] = "dropdown"
        return store
