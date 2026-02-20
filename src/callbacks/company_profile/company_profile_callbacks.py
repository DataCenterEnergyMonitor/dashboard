from dash import Input, Output, State, callback_context, html
import traceback
from dash.exceptions import PreventUpdate
from figures.company_profile.energy_by_company_bar import (
    create_company_profile_bar_plot,
    create_company_energy_use_bar_plot,
)
from figures.company_profile.company_profile_table import create_category_section
from components.figure_card import create_figure_card

_cp_tab1_callback_registered = False
_cp_tab2_callback_registered = False
_cp_tab3_callback_registered = False

# ID prefix for this page's components
ID_PREFIX = "cp-"

# Mapping between actual data values and polished display values
METRIC_MAPPING = {
    "Total company electricity use reporting?": "Company-wide Electricity Usage",
    "Total data center fleet electricity use reporting?": "Data Center Fleet Electricity Usage",
    "Individual data center electricity use reporting?": "Individual Data Center Electricity Usage",
    "Data center fuel use reporting?": "Data Center Fuel Usage",
    "PUE reporting?": "Power Usage Effectiveness (PUE)",
    "Total company water use reporting?": "Company-wide Water Usage",
    "Total data center fleet water use reporting?": "Data Center Fleet Water Usage",
    "Individual data center water use reporting?": "Individual Data Center Water Usage",
    "WUE reporting?": "Water Usage Effectiveness (WUE)",
    "Total company electric power sources reporting?": "Company-wide Power Sources",
    "Data center fleet electric power sources reporting?": "Data Center Fleet Power Sources",
    "Individual data center electric power sources reporting?": "Individual Data Center Power Sources",
    "Third-party standards utilization?": "CDP Reporting",
    "Total company Scope 1 GHG reporting?": "Company-wide Scope 1 Emissions",
    "Data center fleet Scope 1 GHG reporting?": "Data Center Fleet Scope 1 Emissions",
    "Individual data center Scope 1 GHG reporting?": "Individual Data Center Scope 1 Emissions",
    "Total company Scope 2 GHG reporting?": "Company-wide Scope 2 Emissions",
    "Data center fleet Scope 2 GHG reporting?": "Data Center Fleet Scope 2 Emissions",
    "Individual data center Scope 2 GHG reporting?": "Individual Data Center Scope 2 Emissions",
    "Total company Scope 3 GHG reporting?": "Company-wide Scope 3 Emissions",
    "Data center fleet Scope 3 GHG reporting?": "Data Center Fleet Scope 3 Emissions",
    "Individual data center Scope 3 GHG reporting?": "Individual Data Center Scope 3 Emissions",
}

# Metrics organised by category (using raw data values)
METRIC_CATEGORIES = {
    "Energy Reporting": [
        "Total company electricity use reporting?",
        "Total data center fleet electricity use reporting?",
        "Individual data center electricity use reporting?",
        "Data center fuel use reporting?",
        "PUE reporting?",
    ],
    "Water Management": [
        "Total company water use reporting?",
        "Total data center fleet water use reporting?",
        "Individual data center water use reporting?",
        "WUE reporting?",
    ],
    # "Emissions Reporting": [
    #     "Total company Scope 1 GHG reporting?",
    #     "Total company Scope 2 GHG reporting?",
    #     "Total company Scope 3 GHG reporting?",
    #     "Data center fleet Scope 1 GHG reporting?",
    #     "Data center fleet Scope 2 GHG reporting?",
    #     "Data center fleet Scope 3 GHG reporting?",
    # ],
    # "Power Sources": [
    #     "Total company electric power sources reporting?",
    #     "Data center fleet electric power sources reporting?",
    #     "Individual data center electric power sources reporting?",
    # ],
}


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


# ── Tab 1 – Reporting Profile ──────────────────────────────────────────


def register_cp_tab1_callbacks(app, company_profile_df):
    """Register callbacks for Tab 1 - Reporting Profile table."""
    global _cp_tab1_callback_registered
    if _cp_tab1_callback_registered:
        return
    _cp_tab1_callback_registered = True

    @app.callback(
        [
            Output("cp-collapsible-tables-container", "children"),
            Output("cp-company-data-title", "children"),
        ],
        [
            Input(f"{ID_PREFIX}filter-store", "data"),
            Input(f"{ID_PREFIX}active-tab-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def update_cp_tab1(filter_data, active_tab):
        """Update the reporting profile table based on selected company."""
        if active_tab is not None and active_tab != "tab-1":
            raise PreventUpdate

        company = filter_data.get("company") if filter_data else None

        if not company:
            return [], "Select a Company"

        try:
            table_df = company_profile_df[
                company_profile_df["company"] == company
            ].copy()

            category_sections = []
            if not table_df.empty:
                for category, metrics in METRIC_CATEGORIES.items():
                    category_data = []
                    for metric in metrics:
                        metric_row = table_df[table_df["metric"] == metric]
                        if not metric_row.empty:
                            raw_status = metric_row.iloc[0]["status"]
                            status = "Yes" if raw_status in ["Y", "y"] else "No"
                            display_metric = METRIC_MAPPING.get(metric, metric)
                            category_data.append(
                                {"metric": display_metric, "status": status}
                            )

                    if category_data:
                        category_sections.append(
                            create_category_section(category, category_data)
                        )

            title = f"{company} Reporting Profile"
            return category_sections, title

        except Exception as e:
            print(f"Error updating reporting profile: {str(e)}")
            traceback.print_exc()
            return [], "Error Loading Data"

    # Collapsible section toggle callback
    @app.callback(
        [
            #Output("collapse-emissions-reporting", "is_open"),
            Output("collapse-energy-reporting", "is_open"),
            Output("collapse-water-management", "is_open"),
            #Output("collapse-power-sources", "is_open"),
            #Output("chevron-emissions-reporting", "className"),
            Output("chevron-energy-reporting", "className"),
            Output("chevron-water-management", "className"),
            #Output("chevron-power-sources", "className"),
        ],
        [
            #Input("collapse-button-emissions-reporting", "n_clicks"),
            Input("collapse-button-energy-reporting", "n_clicks"),
            Input("collapse-button-water-management", "n_clicks"),
            #Input("collapse-button-power-sources", "n_clicks"),
        ],
        [
            #State("collapse-emissions-reporting", "is_open"),
            State("collapse-energy-reporting", "is_open"),
            State("collapse-water-management", "is_open"),
            #State("collapse-power-sources", "is_open"),
        ],
    )
    def toggle_collapse(
        en_clicks, wm_clicks,
        en_is_open, wm_is_open,
    ):
        ctx = callback_context

        if not ctx.triggered:
            return (
                True, True, #True, True,
                "fas fa-chevron-down",
                "fas fa-chevron-down",
                # "fas fa-chevron-down",
                # "fas fa-chevron-down",
            )

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        states = [en_is_open, wm_is_open]
        icons = [
            "fas fa-chevron-down" if state else "fas fa-chevron-right"
            for state in states
        ]

        if button_id == "collapse-button-energy-reporting":
            states[0] = not states[0]
            icons[0] = "fas fa-chevron-down" if states[0] else "fas fa-chevron-right"
        elif button_id == "collapse-button-water-management":
            states[1] = not states[1]
            icons[1] = "fas fa-chevron-down" if states[1] else "fas fa-chevron-right"

        return *states, *icons


# ── Tab 2 – Energy Trends (energy use over time) ──────────────────────


def register_cp_tab2_callbacks(app, energy_use_df):
    """Register callbacks for Tab 2 - Energy Trends chart."""
    global _cp_tab2_callback_registered
    if _cp_tab2_callback_registered:
        return
    _cp_tab2_callback_registered = True

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


# ── Tab 3 – Energy Comparison (all companies bar chart) ───────────────


def register_cp_tab3_callbacks(app, energy_use_df):
    """Register callbacks for Tab 3 - Energy Comparison chart."""
    global _cp_tab3_callback_registered
    if _cp_tab3_callback_registered:
        return
    _cp_tab3_callback_registered = True

    @app.callback(
        Output("cp-tab3-chart-container", "children"),
        [
            Input(f"{ID_PREFIX}filter-store", "data"),
            Input(f"{ID_PREFIX}active-tab-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def update_cp_tab3(filter_data, active_tab):
        """Update the company comparison bar chart."""
        if active_tab is not None and active_tab != "tab-3":
            raise PreventUpdate

        try:
            fig = create_company_profile_bar_plot(energy_use_df)

            return html.Div(
                [
                    create_figure_card(
                        fig_id="cp-tab3-fig1",
                        title="Electricity Usage by Company",
                        expand_id="expand-cp-tab3-fig1",
                        filename="company_energy_comparison",
                        figure=fig,
                    ),
                ],
                style={"margin": "35px 0"},
            )

        except Exception as e:
            print(f"Error updating energy comparison chart: {str(e)}")
            traceback.print_exc()
            return html.Div(
                create_figure_card(
                    fig_id="cp-tab3-fig1",
                    title="Error",
                    expand_id="expand-cp-tab3-fig1",
                    filename="error",
                    figure=create_empty_chart("Error loading data"),
                ),
                style={"margin": "35px 0"},
            )
