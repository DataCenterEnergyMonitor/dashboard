from dash import Input, Output, callback, no_update, dcc
import dash
import traceback
import pandas as pd
from dash.exceptions import PreventUpdate
from charts.company_profile_barchart import create_company_energy_use_bar_plot

_company_profile_callback_registered = False


def create_company_profile_callback(app, data_dict, chart_configs):
    """Create callback for the company profile page"""
    print("Registering company profile callback")

    @app.callback(
        [
            Output("company-profile-bar-chart", "figure"),
            Output("company-profile-data-table", "data"),
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

        print(f"Updating company profile with company: {company}")

        try:
            chart_df = data_dict["company-profile-bar"]["df"].copy()
            table_df = data_dict["company-profile-table"]["df"].copy()

            # Set default title
            title = "Select a Company"

            # Filter data based on selected company
            if company:
                chart_df = chart_df[chart_df["company_name"] == company]
                table_df = table_df[table_df["company"] == company]
                title = f"{company} Profile"

            figure = create_company_energy_use_bar_plot(chart_df)
            # Only include metric and status columns in the table data
            table_data = table_df[["metric", "status"]].to_dict("records")

            if chart_df.empty and table_df.empty:
                print("No data available after applying filters")
                return (
                    create_empty_chart("No data available for selected filters"),
                    [],
                    "No Data Available",
                )

            return figure, table_data, title

        except Exception as e:
            print(f"Error updating company profile: {str(e)}")
            traceback.print_exc()
            return (
                create_empty_chart("Error loading data"),
                [],
                "Error Loading Data",
            )


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
