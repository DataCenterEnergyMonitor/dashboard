"""Callback for Company Profile Tab 2 – Energy Trends."""

from pathlib import Path
from dash import Input, Output, State, html
import traceback
from dash.exceptions import PreventUpdate
from figures.company_profile.energy_by_year_bar import (
    create_company_energy_use_bar_plot,
)
from components.figure_card import create_figure_card
from components.excel_export import create_filtered_excel_download

# ID prefix for this page's components
ID_PREFIX = "cp-"

_registered = False


def create_empty_chart(message):
    return {
        "data": [],
        "layout": {
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
            "annotations": [
                {
                    "text": message,
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 20},
                }
            ],
            "plot_bgcolor": "white",
            "paper_bgcolor": "white",
        },
    }


def register_cp_tab2_callbacks(app, energy_use_df):
    """Register callbacks for Tab 2 - Energy Trends chart."""
    global _registered
    if _registered:
        return
    _registered = True

    # ── Chart update ────────────────────────────────────────────────────
    @app.callback(
        Output("cp-tab2-chart-container", "children"),
        [
            Input(f"{ID_PREFIX}filter-store", "data"),
            Input(f"{ID_PREFIX}active-tab-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def update_cp_tab2(filter_data, active_tab):
        """Update the energy-over-time chart for the selected company."""
        if active_tab is not None and active_tab != "tab-2":
            raise PreventUpdate

        company = filter_data.get("company") if filter_data else None

        try:
            if company:
                company_df = energy_use_df[
                    energy_use_df["company_name"] == company
                ].copy()
                if not company_df.empty:
                    fig = create_company_energy_use_bar_plot(company_df)
                else:
                    fig = create_empty_chart(
                        f"No energy data available for {company}"
                    )
                title = f"{company} — Energy Consumption Over Time"
            else:
                fig = create_empty_chart("Select a company to view data")
                title = "Energy Consumption Over Time"

            return html.Div(
                [
                    create_figure_card(
                        fig_id="cp-tab2-fig1",
                        title=title,
                        expand_id="expand-cp-tab2-fig1",
                        filename="company_energy_trends",
                        figure=fig,
                    ),
                ],
                style={"margin": "35px 0"},
            )

        except Exception as e:
            print(f"Error updating energy trends chart: {str(e)}")
            traceback.print_exc()
            return html.Div(
                create_figure_card(
                    fig_id="cp-tab2-fig1",
                    title="Error",
                    expand_id="expand-cp-tab2-fig1",
                    filename="error",
                    figure=create_empty_chart("Error loading data"),
                ),
                style={"margin": "35px 0"},
            )

    # ── Expand modal ────────────────────────────────────────────────────
    @app.callback(
        [
            Output("cp-tab2-fig1-modal", "is_open"),
            Output("cp-tab2-fig1-modal-title", "children"),
            Output("cp-tab2-expanded-fig1", "figure"),
        ],
        [Input("expand-cp-tab2-fig1", "n_clicks")],
        [
            State("cp-tab2-fig1-modal", "is_open"),
            State("cp-tab2-fig1", "figure"),
        ],
        prevent_initial_call=True,
    )
    def toggle_cp_tab2_modal(expand_clicks, is_open, current_figure):
        if not expand_clicks:
            raise PreventUpdate
        return (
            not is_open,
            "Energy Consumption Over Time",
            current_figure or {},
        )

    # ── Download data ───────────────────────────────────────────────────
    @app.callback(
        Output("download-cp-tab2-fig1", "data"),
        Input("download-btn-cp-tab2-fig1", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_cp_tab2_data(n_clicks):
        root_dir = Path(__file__).parent.parent.parent.parent
        input_path = root_dir / "data" / "modules.xlsx"

        return create_filtered_excel_download(
            input_path=input_path,
            output_filename="company_energy_trends.xlsx",
            sheets_to_export=["Data Center Electricity Use ","Company Total Electricity Use", "Read Me"],
            internal_prefix="_internal_",
            n_clicks=n_clicks,
        )
