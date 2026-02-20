import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import os
import dash
from dash import Dash, dcc, html, Input, Output, callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from helpers.export_json_for_quarto import export_json_for_quarto

from data_loader import (
    load_pue_data,
    load_wue_data,
    create_pue_wue_data,
    load_pue_wue_companies_data,
    load_energyprojections_data,
    load_gp_data,
    transpose_gp_data,
    load_reporting_data,
    load_energy_use_data,
    load_company_profile_data,
    update_metadata,
)

from pages.pue_wue.pue_wue_page import create_pue_wue_page
from pages.pue_wue.pue_methods_page import create_pue_methodology_page
from pages.pue_wue.wue_methods_page import create_wue_methodology_page
from pages.pue_wue.pue_data_page import create_pue_data_page
from pages.pue_wue.wue_data_page import create_wue_data_page
from pages.energy_projections.energy_projections import create_energy_projections_page
from pages.energy_projections.energy_projections_methods import (
    create_energy_projections_methodology_page,
)
from pages.energy_projections.energy_projections_data import create_energy_projections_data_page

from pages.water_projections.water_projections_page import create_water_projections_page
from pages.water_projections.water_projections_methods_page import (
    create_water_projections_methodology_page,
)
from pages.water_projections.water_projections_data_page import create_water_projections_data_page
from pages.global_policies.gp_main_page import create_gp_page
from pages.reporting_trends.rt_main_page import create_rt_page
from pages.company_profile.cp_main_page import create_cp_page
from pages.home import create_home_page
from pages.common.about import create_about_page
from pages.common.companies import create_companies_page
from pages.common.contact import create_contact_page
from pages.learn.data_centers_101 import create_data_centers_101_page

from callbacks.company_profile.cp_page_callback import register_cp_page_callbacks
from callbacks.company_profile.cp_filter_callbacks import register_cp_filter_callbacks
from callbacks.company_profile.cp_tab1_callback import register_cp_tab1_callbacks
from callbacks.company_profile.cp_tab2_callback import register_cp_tab2_callbacks
from callbacks.company_profile.cp_tab3_callback import register_cp_tab3_callbacks
from callbacks.pue_wue.pue_wue_page_callbacks import register_pue_wue_callbacks
from callbacks.energy_projections.ep_page_callbacks import (
    register_energy_projections_callbacks,
)
from callbacks.water_projections.water_projections_page_callbacks import (
    register_water_projections_callbacks,
)
from callbacks.global_policies.gp_page_callback import (
    register_gp_page_callbacks,
)
from callbacks.global_policies.gp_tab1_callback import register_gp_tab1_callbacks
from callbacks.global_policies.gp_tab2_callback import register_gp_tab2_callbacks
from callbacks.global_policies.gp_tab3_callback import register_gp_tab3_callbacks
from callbacks.reporting_trends.rt_page_callback import (
    register_rt_page_callbacks,
)
from callbacks.reporting_trends.rt_filter_callbacks import (
    register_rt_filter_callbacks,
)
from callbacks.reporting_trends.rt_tab1_callback import (
    register_rt_tab1_callbacks,
)
from callbacks.reporting_trends.rt_tab2_callback import (
    register_rt_tab2_callbacks,
)
from callbacks.reporting_trends.rt_tab3_callback import (
    register_rt_tab3_callbacks,
)
from callbacks.reporting_trends.rt_tab4_callback import (
    register_rt_tab4_callbacks,
)
from callbacks.reporting_trends.rt_tab5_callback import (
    register_rt_tab5_callbacks,
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
            "https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap",
            "https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500;700&display=swap",
        ],
        suppress_callback_exceptions=True,
        assets_folder=assets_path,  # Set absolute path to assets
        assets_url_path="assets",  # Explicitly set the assets URL path
    )

    # Load data
    pue_df = load_pue_data()
    wue_df = load_wue_data()
    pue_wue_df = create_pue_wue_data(pue_df, wue_df)
    pue_wue_companies_df = load_pue_wue_companies_data()
    print("Companies", pue_wue_companies_df[pue_wue_companies_df["company_name"].isin(["LY Corporation", "SDC SpaceNet", "Quantum Switch Tamasuk","Quantum Switch"])][["company_name","year_founded", "year","reports_pue", "reports_wue"]])
    energyprojections_df = load_energyprojections_data()
    waterprojections_df = (
        load_energyprojections_data()
    )  # TO DO: replace with the function to load water projections dataset
    gp_base_df, globalpolicies_df = load_gp_data()
    gp_transposed_df = transpose_gp_data(globalpolicies_df)
    reporting_df = load_reporting_data()
    print("Test-Tets: Reporting_df")
    print(reporting_df["reporting_status"].unique())
    print(reporting_df[reporting_df["reporting_status"] == "Pending Data Submission"].head(10))
    energy_use_df = load_energy_use_data()
    company_profile_df = load_company_profile_data()

    # Update last modified timestamp for each imported dataset
    update_metadata()

    # Export Datasets metadata to quarto parameters
    export_json_for_quarto()

    # DELETE
    # Read and print metadata to check
    import json
    from pathlib import Path

    json_path = Path("data") / "dependencies" / "metadata.json"

    with open(json_path, "r") as f:
        metadata = json.load(f)

    # Pretty-print
    import pprint

    pprint.pprint(metadata)

    # Initialize callbacks
    register_pue_wue_callbacks(app, pue_wue_df)
    register_energy_projections_callbacks(app, energyprojections_df)
    register_water_projections_callbacks(app, waterprojections_df)
    register_gp_page_callbacks(app, gp_base_df, globalpolicies_df)
    register_gp_tab1_callbacks(app, globalpolicies_df)
    # Use the transposed dataframe (with attr_type/attr_value) for Tab 2 callbacks
    register_gp_tab2_callbacks(app, gp_transposed_df)
    register_gp_tab3_callbacks(app, gp_transposed_df)
    # Company Reporting Trends page callbacks
    register_rt_page_callbacks(app, reporting_df, pue_wue_companies_df)
    # Centralized filter callbacks for Reporting Trends (all tabs)
    register_rt_filter_callbacks(app)
    register_rt_tab1_callbacks(app, reporting_df)
    register_rt_tab2_callbacks(app, reporting_df, pue_wue_companies_df)
    register_rt_tab3_callbacks(app, reporting_df, pue_wue_companies_df)
    register_rt_tab4_callbacks(app, pue_wue_companies_df)
    register_rt_tab5_callbacks(app, reporting_df, pue_wue_companies_df)

    # Company Profile page callbacks (new tab-based structure)
    cp_companies = sorted(energy_use_df["company_name"].unique())
    cp_default_company = cp_companies[0] if cp_companies else None
    register_cp_page_callbacks(app, cp_companies, cp_default_company, energy_use_df)
    register_cp_filter_callbacks(app)
    register_cp_tab1_callbacks(app, company_profile_df)
    register_cp_tab2_callbacks(app, energy_use_df)
    register_cp_tab3_callbacks(app, energy_use_df)

    # URL Routing
    app.layout = html.Div(
        [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
    )

    # Create the data sources dictionary for KPI cards
    kpi_data_sources = {
        "pue": pue_df,
        "wue": wue_df,
        "company_name": pue_wue_df,
        "energy_projections_studies": energyprojections_df,  # TO DO: add water projections studies to the KPIs count
    }

    @app.callback(Output("page-content", "children"), Input("url", "pathname"))
    def display_page(pathname):
        print(f"\nRouting request for pathname: '{pathname}'")  # Debug print
        if pathname == "/pue-wue":
            return create_pue_wue_page(app, pue_wue_df)
        elif pathname == "/pue-methodology":
            return create_pue_methodology_page()
        elif pathname == "/wue-methodology":
            return create_wue_methodology_page()
        elif pathname == "/pue-data":
            return create_pue_data_page()
        elif pathname == "/wue-data":
            return create_wue_data_page()
        elif pathname == "/energy-projections":
            return create_energy_projections_page(app, energyprojections_df)
        elif pathname == "/energy-projections-methodology":
            return create_energy_projections_methodology_page()
        elif pathname == "/energy-projections-data":
            return create_energy_projections_data_page()
        elif pathname == "/water-projections":
            return create_water_projections_page(app, waterprojections_df)
        elif pathname == "/water-projections-methodology":
            return create_water_projections_methodology_page()
        elif pathname == "/water-projections-data":
            return create_water_projections_data_page()
        elif pathname == "/global-policies":
            return create_gp_page(app, globalpolicies_df)
        elif pathname == "/reporting-trends":
            return create_rt_page(app, reporting_df, pue_wue_companies_df)
        elif pathname == "/company-profile":
            return create_cp_page(app, company_profile_df, energy_use_df)
        elif pathname == "/about":
            return create_about_page()
        elif pathname == "/companies":
            return create_companies_page()
        elif pathname == "/contact":
            return create_contact_page()
        elif pathname == "/data-centers-101":
            return create_data_centers_101_page()
        else:
            print(f"No route match, defaulting to home page")  # Debug print
            return create_home_page(kpi_data_sources)

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
    #app.run_server(debug=True)
    app.run(debug=True)
