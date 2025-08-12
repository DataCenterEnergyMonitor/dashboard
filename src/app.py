import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import os
import dash
from dash import Dash, dcc, html, Input, Output, callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from data_loader import (
    load_pue_data,
    load_wue_data,
    create_pue_wue_data,
    load_energyforecast_data,
    load_reporting_data,
    load_energy_use_data,
    load_company_profile_data,
)

from pages.pue_page import create_pue_page
from pages.wue_page import create_wue_page
from pages.pue_wue_page import create_pue_wue_page
from pages.pue_methods_page import create_pue_methodology_page
from pages.wue_methods_page import create_wue_methodology_page
from pages.pue_data_page import create_pue_data_page
from pages.wue_data_page import create_wue_data_page
from pages.company_profile_page import create_company_profile_page
from pages.home_page import create_home_page
from pages.about_page import create_about_page
from pages.contact_page import create_contact_page
from pages.energy_forecast_page import create_forecast_page
from pages.reporting_page import create_reporting_page
from pages.data_centers_101_page import create_data_centers_101_page
from pages.energy_use_page import create_energy_use_page

from charts.pue_chart import create_pue_scatter_plot
from charts.wue_chart import create_wue_scatter_plot
from charts.forecast_chart import create_forecast_scatter_plot
from charts.reporting_barchart import create_reporting_bar_plot
from charts.timeline_chart import create_timeline_bar_plot
from charts.energy_use_barchart import create_energy_use_bar_plot
from charts.company_profile_barchart import create_company_profile_bar_plot
from callbacks.base_chart_callback import create_chart_callback
from callbacks.reporting_callbacks import (
    create_reporting_callback,
    create_reporting_download_callback,
)
from callbacks.energy_use_callbacks import (
    create_energy_use_callback,
    create_energy_use_download_callback,
)
from callbacks.company_profile_callbacks import (
    create_company_profile_callback,
    create_company_profile_download_callback,
)
from callbacks.pue_wue_page_callback import (
    register_pue_wue_callbacks
)
from components.kpi_data_cards import create_kpi_cards


def create_app():
    # Get absolute path to assets folder
    assets_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "assets")
    )

    for root, dirs, files in os.walk(assets_path):
        for file in files:
            file_path = os.path.join(root, file)

    app = Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://use.fontawesome.com/releases/v5.15.4/css/all.css",
            "https://fonts.googleapis.com/css2?family=Oswald:wght@400;700&family=Montserrat:wght@400;500;600;700&family=Poppins:wght@400;500&family=Inter:wght@400;500&display=swap",
            "https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700&family=Roboto:wght@400;500&display=swap",
        ],
        suppress_callback_exceptions=True,
        assets_folder=assets_path,  # Set absolute path to assets
        assets_url_path="assets",  # Explicitly set the assets URL path
    )


    # Load data
    pue_df = load_pue_data()
    print("PUE DataFrame loaded successfully", pue_df.shape)
    print(pue_df.info())  # Display first 5 rows for debugging
    print(pue_df.head())  # Display first 5 rows for debugging
    wue_df = load_wue_data()
    pue_wue_df = create_pue_wue_data(pue_df, wue_df)
    print("PUE-WUE DataFrame loaded successfully", pue_df.shape)
    print(pue_wue_df.info())  # Display first 5 rows for debugging
    print(pue_wue_df.head())  # Display first 5 rows for debugging
    forecast_df, forecast_avg = load_energyforecast_data()
    reporting_df = load_reporting_data()
    energy_use_df = load_energy_use_data()
    company_profile_df = load_company_profile_data()
    # Create data dictionary for charts
    data_dict = {
        "pue-scatter": {"df": pue_df, "industry_avg": None},
        "wue-scatter": {"df": wue_df, "industry_avg": None},
        "forecast-scatter": {"df": forecast_df, "industry_avg": None},
        "reporting-bar": {"df": reporting_df},
        "timeline-bar": {"df": reporting_df},
        "energy-use-bar": {"df": energy_use_df},
        "company-profile-bar": {"df": energy_use_df},
        "company-profile-table": {"df": company_profile_df},
    }

    # Define chart configurations
    chart_configs = {
        "pue-scatter": {
            "base_id": "pue",
            "chart_id": "pue-scatter-chart",
            "chart_creator": create_pue_scatter_plot,
            "filename": "pue-data.csv",
            "filters": [
                "facility_scope",
                "company",
                "iea_region",
                "iecc_climate_zone_s_",
                "pue_measurement_level",
            ],
            "download_id": "download-pue-data",  # Add download button ID
        },
        "wue-scatter": {
            "base_id": "wue",
            "chart_id": "wue-scatter-chart",
            "chart_creator": create_wue_scatter_plot,
            "filename": "wue-data.csv",
            "filters": ["facility_scope", "company"],
            "download_id": "download-wue-data",  # Add download button ID
        },
        "forecast-scatter": {
            "base_id": "forecast",
            "chart_id": "forecast-scatter-chart",
            "chart_creator": create_forecast_scatter_plot,
            "filename": "forecast-data.csv",
            "filters": ["geographic_scope", "peer_reviewed_", "author_type_s_"],
            "download_id": "download-forecast-data",  # Add download button ID
        },
        "reporting-bar": {
            "base_id": "reporting",
            "chart_id": "reporting-bar-chart",
            "chart_creator": create_reporting_bar_plot,
            "filename": "reporting-data.csv",
            "filters": ["from_year", "to_year"],
            "download_id": "download-reporting-data",  # Add download button ID
        },
        "timeline-bar": {  # Add timeline chart config
            "base_id": "reporting",
            "chart_id": "timeline-bar-chart",
            "chart_creator": create_timeline_bar_plot,
            "filename": "reporting-data.csv",
            "filters": ["from_year", "to_year"],
        },
        "energy-use-bar": {
            "base_id": "energy-use-bar",
            "chart_id": "energy-use-bar-chart",
            "chart_creator": create_energy_use_bar_plot,
            "filename": "energy-use-data.csv",
            "filters": ["reported_data_year", "reporting_scope", "company_name"],
            "download_id": "download-energy-use-data",
        },
        "company-profile-bar": {
            "base_id": "company-profile",
            "chart_id": "company-profile-bar-chart",
            "chart_creator": create_company_profile_bar_plot,
            "filename": "company-profile-data.csv",
            "filters": ["company_name"],
            "download_id": "download-company-profile-data",
        },
    }

    # Initialize callbacks
    register_pue_wue_callbacks(app, pue_wue_df)

    #pue_callback = create_chart_callback(app, data_dict, chart_configs["pue-scatter"])
    #wue_callback = create_chart_callback(app, data_dict, chart_configs["wue-scatter"])
    forecast_callback = create_chart_callback(
        app, data_dict, chart_configs["forecast-scatter"]
    )
    reporting_callback = create_reporting_callback(app, data_dict, chart_configs)
    reporting_download_callback = create_reporting_download_callback(app, data_dict)
    energy_use_callback = create_energy_use_callback(
        app, data_dict, chart_configs["energy-use-bar"]
    )
    energy_use_download_callback = create_energy_use_download_callback(app, data_dict)
    company_profile_callback = create_company_profile_callback(
        app, data_dict, chart_configs["company-profile-bar"]
    )
    company_profile_download_callback = create_company_profile_download_callback(
        app, data_dict
    )

    # URL Routing
    app.layout = html.Div(
        [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
    )

    @app.callback(Output("page-content", "children"), Input("url", "pathname"))
    def display_page(pathname):
        print(f"\nRouting request for pathname: '{pathname}'")  # Debug print
        if pathname == "/pue":
            return create_pue_page(app, pue_df)
        elif pathname == "/wue":
            return create_wue_page(app, wue_df)
        elif pathname == "/pue_wue":
            return create_pue_wue_page(app, pue_wue_df)
        elif pathname == '/pue-methodology':  
            return create_pue_methodology_page()
        elif pathname == '/wue-methodology':  
            return create_wue_methodology_page()
        elif pathname == '/pue-data':  
            return create_pue_data_page()
        elif pathname == '/wue-data':  
            return create_wue_data_page()
        elif pathname == "/forecast": 
            print("Creating forecast page")  # Debug print
            return create_forecast_page(app, forecast_df)
        elif pathname == "/reporting":
            return create_reporting_page(app, reporting_df, data_dict, chart_configs)
        elif pathname == "/energy-use":
            return create_energy_use_page(app, energy_use_df)
        elif pathname == "/company-profile":
            return create_company_profile_page(app, company_profile_df, energy_use_df)
        elif pathname == "/about":
            return create_about_page()
        elif pathname == "/contact":
            return create_contact_page()
        elif pathname == "/data-centers-101":
            return create_data_centers_101_page()
        else:
            print(f"No route match, defaulting to home page")  # Debug print
            return create_home_page(pue_wue_df)

    # Navbar toggle callback
    @app.callback(
        Output("navbar-collapse", "is_open"),
        [Input("navbar-toggler", "n_clicks")],
        [State("navbar-collapse", "is_open")],
    )
    def toggle_navbar_collapse(n, is_open):
        if n:
            return not is_open
        return is_open

    return app

if __name__ == "__main__":
    app = create_app()
    app.run_server(debug=True)
