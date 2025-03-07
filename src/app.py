import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import os

import dash
from dash import Dash, dcc, html, Input, Output, callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from data_loader import load_pue_data, load_wue_data, load_energyforecast_data, load_reporting_trends_data

from pages.pue_page import create_pue_page
from pages.wue_page import create_wue_page
from pages.home_page import create_home_page
from pages.about_page import create_about_page
from pages.energy_forecast_page import create_forecast_page
from pages.reporting_trends_page import create_reporting_trends_page

from callbacks.chart_callbacks import ChartCallbackManager
from charts.pue_chart import create_pue_scatter_plot
from charts.wue_chart import create_wue_scatter_plot
from charts.forecast_chart import create_forecast_scatter_plot
from charts.reporting_barchart import create_reporting_bar_plot

def create_app():
    # Get absolute path to assets folder
    assets_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))
    
    # Debug logging
    print(f"Current working directory: {os.getcwd()}")
    print(f"Assets folder path: {assets_path}")
    print(f"Assets folder exists: {os.path.exists(assets_path)}")
    
    # List all files in assets directory
    print("\nFiles in assets directory:")
    for root, dirs, files in os.walk(assets_path):
        for file in files:
            file_path = os.path.join(root, file)
            print(f"File: {file_path}")
            print(f"File exists: {os.path.exists(file_path)}")
            print(f"File permissions: {oct(os.stat(file_path).st_mode)[-3:]}")

    app = Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True,
        assets_folder=assets_path,  # Set absolute path to assets
        assets_url_path='assets'    # Explicitly set the assets URL path
    )

    # Load data
    pue_df, company_counts, pue_industry_avg = load_pue_data()
    wue_df, wue_company_counts, wue_industry_avg = load_wue_data()
    forecast_df,forecast_avg = load_energyforecast_data()

    # Create data dictionary for charts
    data_dict = {
        'pue-scatter': {
            'df': pue_df,
            'industry_avg': None
        },
        'wue-scatter': {
            'df': wue_df,
            'industry_avg': None
        },
        'forecast-scatter': {
            'df': forecast_df,
            'industry_avg': forecast_avg
        }    
    }

    # Define chart configurations
    chart_configs = {
        'pue-scatter': {
            'base_id': 'pue', #which filters to use
            'chart_id': 'pue-scatter-chart',
            'chart_creator': create_pue_scatter_plot,
            'filename': 'pue-data.csv',
            'filters': ['facility_scope', 'company', 'iea_region', 'iecc_climate_zone_s_', 'pue_measurement_level']
        },
        'wue-scatter': {
            'base_id': 'wue',
            'chart_id': 'wue-scatter-chart',
            'chart_creator': create_wue_scatter_plot,
            'filename': 'wue-data.csv',
            'filters': ['facility_scope', 'company']
        },
        'forecast-scatter': {
            'base_id': 'energy',
            'chart_id': 'forecast-scatter-chart',
            'chart_creator': create_forecast_scatter_plot,
            'filename': 'forecast-data.csv',
            'filters': ['geographic_scope', 'peer_reviewed_', 'author_type_s_']
        }
    }

    # Initialize chart callback manager
    chart_manager = ChartCallbackManager(app, data_dict, chart_configs)

    # URL Routing
    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ])
    
    @app.callback(
        Output('page-content', 'children'),
        Input('url', 'pathname')
    )
    def display_page(pathname):
        if pathname == '/pue':
            return create_pue_page(app, pue_df, company_counts)
        elif pathname == '/wue':
            return create_wue_page(app, wue_df, wue_company_counts)
        elif pathname == '/energy':
            return create_forecast_page(app, forecast_df)
        elif pathname == '/reporting':
            return create_reporting_trends_page(app, reporting_df)
        elif pathname == '/about':
            return create_about_page()
        elif pathname == '/data_centers_101':
            return create_data_centers_101_page()
        else:
            return create_home_page()

    # Navbar toggle callback - moved inside create_app()
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

if __name__ == '__main__':
    app = create_app()
    app.run_server(debug=True)