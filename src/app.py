import dash
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from data_loader import load_pue_data, load_wue_data
from pages.pue_page import create_pue_page
from pages.wue_page import create_wue_page
from pages.home_page import create_home_page
from pages.about_page import create_about_page
from callbacks.chart_callbacks import ChartCallbackManager
from charts.pue_chart import create_pue_scatter_plot
from charts.wue_chart import create_wue_scatter_plot

def create_app():
    app = dash.Dash(
        __name__,
        external_stylesheets=[
            'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap',
            dbc.themes.BOOTSTRAP
        ],
        suppress_callback_exceptions=True
    )

    # Load data
    pue_df, company_counts, pue_industry_avg = load_pue_data()
    wue_df, wue_company_counts, wue_industry_avg = load_wue_data()

    # Create data dictionary for charts
    data_dict = {
        'pue-scatter': {
            'df': pue_df,
            'industry_avg': pue_industry_avg
        },
        'wue-scatter': {
            'df': wue_df,
            'industry_avg': wue_industry_avg
        }
    }

    # Define chart configurations
    chart_configs = {
        'pue-scatter': {
            'base_id': 'pue',
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
        elif pathname == '/data_centers_101':
            return create_about_page()
        else:
            return create_home_page()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run_server(debug=True)