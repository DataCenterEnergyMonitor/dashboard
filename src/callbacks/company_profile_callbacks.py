from dash import Input, Output, callback, no_update, dcc, State, callback_context
import dash
import traceback
import pandas as pd
from dash.exceptions import PreventUpdate
from charts.company_profile_barchart import create_company_energy_use_bar_plot
from components.company_profile_table import create_category_section

_company_profile_callback_registered = False


def create_company_profile_callback(app, data_dict, chart_configs):
    """Create callback for the company profile page"""
    print("Registering company profile callback")

    # Define mapping between actual data values and polished display values
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

    # Define metrics with their categories using the actual data values
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
        "Emissions Reporting": [
            "Total company Scope 1 GHG reporting?",
            "Total company Scope 2 GHG reporting?",
            "Total company Scope 3 GHG reporting?",
            "Data center fleet Scope 1 GHG reporting?",
            "Data center fleet Scope 2 GHG reporting?",
            "Data center fleet Scope 3 GHG reporting?",
        ],
        "Power Sources": [
            "Total company electric power sources reporting?",
            "Data center fleet electric power sources reporting?",
            "Individual data center electric power sources reporting?",
        ],
    }

    @app.callback(
        [
            Output("company-profile-bar-chart", "figure"),
            Output("collapsible-tables-container", "children"),
            Output("company-data-title", "children"),
        ],
        [
            Input("url", "pathname"),
            Input("company-profile-dropdown", "value"),
        ],
    )
    def update_company_profile(pathname, company):
        if pathname != "/company-profile":
            raise PreventUpdate

        try:
            # Initialize with empty data
            figure = create_empty_chart("Select a company to view data")
            table_data = []
            title = "Select a Company"

            if company:
                # Filter data for selected company
                chart_df = data_dict["company-profile-bar"]["df"][
                    data_dict["company-profile-bar"]["df"]["company_name"] == company
                ].copy()

                table_df = data_dict["company-profile-table"]["df"][
                    data_dict["company-profile-table"]["df"]["company"] == company
                ].copy()

                if not table_df.empty:
                    # Process each category and create collapsible sections
                    category_sections = []
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

                        if category_data:  # Only create section if there's data
                            category_sections.append(
                                create_category_section(category, category_data)
                            )

                # Create chart figure if we have data
                if not chart_df.empty:
                    figure = create_company_energy_use_bar_plot(chart_df)

                title = f"{company} Profile"

                return figure, category_sections, title

            return figure, [], title

        except Exception as e:
            print(f"Error updating company profile: {str(e)}")
            traceback.print_exc()
            return (
                create_empty_chart("Error loading data"),
                [],
                "Error Loading Data",
            )

    @app.callback(
        [
            Output("collapse-emissions-reporting", "is_open"),
            Output("collapse-energy-reporting", "is_open"),
            Output("collapse-water-management", "is_open"),
            Output("collapse-power-sources", "is_open"),
            Output("chevron-emissions-reporting", "className"),
            Output("chevron-energy-reporting", "className"),
            Output("chevron-water-management", "className"),
            Output("chevron-power-sources", "className"),
        ],
        [
            Input("collapse-button-emissions-reporting", "n_clicks"),
            Input("collapse-button-energy-reporting", "n_clicks"),
            Input("collapse-button-water-management", "n_clicks"),
            Input("collapse-button-power-sources", "n_clicks"),
        ],
        [
            State("collapse-emissions-reporting", "is_open"),
            State("collapse-energy-reporting", "is_open"),
            State("collapse-water-management", "is_open"),
            State("collapse-power-sources", "is_open"),
        ],
    )
    def toggle_collapse(
        em_clicks,
        en_clicks,
        wm_clicks,
        ps_clicks,
        em_is_open,
        en_is_open,
        wm_is_open,
        ps_is_open,
    ):
        ctx = callback_context

        if not ctx.triggered:
            return (
                True,
                True,
                True,
                True,
                "fas fa-chevron-down",
                "fas fa-chevron-down",
                "fas fa-chevron-down",
                "fas fa-chevron-down",
            )

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Initialize all states with current values
        states = [em_is_open, en_is_open, wm_is_open, ps_is_open]
        icons = [
            "fas fa-chevron-down" if state else "fas fa-chevron-right"
            for state in states
        ]

        # Update the appropriate state based on which button was clicked
        if button_id == "collapse-button-emissions-reporting":
            states[0] = not states[0]
            icons[0] = "fas fa-chevron-down" if states[0] else "fas fa-chevron-right"
        elif button_id == "collapse-button-energy-reporting":
            states[1] = not states[1]
            icons[1] = "fas fa-chevron-down" if states[1] else "fas fa-chevron-right"
        elif button_id == "collapse-button-water-management":
            states[2] = not states[2]
            icons[2] = "fas fa-chevron-down" if states[2] else "fas fa-chevron-right"
        elif button_id == "collapse-button-power-sources":
            states[3] = not states[3]
            icons[3] = "fas fa-chevron-down" if states[3] else "fas fa-chevron-right"

        return *states, *icons


def register_company_profile_callbacks(app, data_dict, chart_configs):
    """Register callbacks for the company profile page"""
    global _company_profile_callback_registered
    if _company_profile_callback_registered:
        return

    print("Attempting to register company profile callbacks...")
    print("Called from:")
    for line in traceback.format_stack()[:-1]:
        print(line.strip())

    # Register the main chart callback
    create_company_profile_callback(app, data_dict, chart_configs)
    _company_profile_callback_registered = True
    print("Successfully registered company profile callbacks")


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


def create_company_profile_download_callback(app, data_dict):
    """Create download callback for company profile data"""

    @app.callback(
        Output("download-company-profile-data", "data"),
        Input("btn-download-company-profile-data", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_company_profile_data(n_clicks):
        if n_clicks is None:
            raise PreventUpdate
        df = data_dict["company-profile-data"]["df"]
        return dcc.send_data_frame(df.to_csv, "company_profile_data.csv", index=False)
