import dash
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from data_loader import load_pue_data, load_wue_data
from pages.home_page import create_home_page
from pages.pue_page import create_pue_page
from pages.wue_page import create_wue_page
from pages.about_page import create_about_page
from callbacks.chart_callbacks import ChartCallbackManager
from charts.pue_chart import create_pue_scatter_plot
from charts.wue_chart import create_wue_scatter_plot  # Add WUE chart import

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

    # Create data dictionary for each chart type
    data_dict = {
        'pue': {
            'df': pue_df,
            'industry_avg': pue_industry_avg,
            'value_column': 'real_pue'  # Add column name for the metric
        },
        'wue': {
            'df': wue_df,
            'industry_avg': wue_industry_avg,
            'value_column': 'wue'  # Add column name for the metric
        }
    }

    # Define chart configurations
    chart_configs = {
        'pue': {
            'chart_id': 'pue-scatter-chart',
            'company_dropdown_id': 'pue-company-dropdown',
            'scope_dropdown_id': 'pue-facility-scope-dropdown',
            'geographical_scope_dropdown_id': 'pue-geographical-scope-dropdown',
            'chart_creator': create_pue_scatter_plot,
            'download_data_id': 'pue-download-dataframe',
            'download_button_id': 'pue-download-button',
            'filename': 'pue_data.csv',
            'chart_type': 'pue' # chart type identifier
        },
        'wue': {
            'chart_id': 'wue-scatter-chart',
            'company_dropdown_id': 'wue-company-dropdown',
            'scope_dropdown_id': 'wue-facility-scope-dropdown',
            'geographical_scope_dropdown_id': 'wue-geographical-scope-dropdown',
            'chart_creator': create_wue_scatter_plot,
            'download_data_id': 'wue-download-dataframe',
            'download_button_id': 'wue-download-button',
            'filename': 'wue_data.csv',
            'chart_type': 'wue'  # Add chart type identifier
        }
    }

    # Initialize callback manager with both data and configurations
    callback_manager = ChartCallbackManager(app, data_dict, chart_configs)

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
            return create_pue_page(pue_df, company_counts)
        elif pathname == '/wue':
            return create_wue_page(wue_df, wue_company_counts)
        elif pathname == '/about':
            return create_about_page()
        else:
            return create_home_page()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run_server(debug=True)