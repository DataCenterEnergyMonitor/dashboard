"""Callback for Company Profile Tab 1 - Reporting Profile (AG Grid tables)."""

from dash import Input, Output, html
import traceback
from dash.exceptions import PreventUpdate
from figures.company_profile.company_profile_table import (
    create_reporting_profile_section,
)

# ID prefix for this page's components
ID_PREFIX = "cp-"

_registered = False


def register_cp_tab1_callbacks(app, company_profile_df):
    """Register callbacks for Tab 1 - Reporting Profile AG Grids."""
    global _registered
    if _registered:
        return
    _registered = True

    @app.callback(
        Output("cp-tab1-container", "children"),
        [
            Input(f"{ID_PREFIX}filter-store", "data"),
            Input(f"{ID_PREFIX}active-tab-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def update_cp_tab1(filter_data, active_tab):
        """Render the reporting profile grids for the selected company."""
        if active_tab is not None and active_tab != "tab-1":
            raise PreventUpdate

        company = filter_data.get("company") if filter_data else None

        if not company:
            return html.Div(
                "Select a company to view its reporting profile.",
                style={
                    "padding": "40px",
                    "color": "#6c757d",
                    "fontFamily": "Inter",
                    "fontSize": "16px",
                },
            )

        try:
            table_df = company_profile_df[
                company_profile_df["company"] == company
            ].copy()

            title = f"{company} Reporting Profile"

            return html.Div(
                [
                    html.H5(
                        title,
                        className="text-left",
                        style={"padding": "0px 15px", "marginBottom": "0px"},
                    ),
                    create_reporting_profile_section(table_df),
                ],
                style={"margin": "35px 0"},
            )

        except Exception as e:
            print(f"Error updating reporting profile: {str(e)}")
            traceback.print_exc()
            return html.Div(
                "Error loading reporting profile.",
                style={"padding": "40px", "color": "#dc2626"},
            )
