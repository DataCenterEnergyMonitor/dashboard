import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import dash
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from data_loader import load_pue_data, load_wue_data, load_energyforecast_data
from pages.pue_page import create_pue_page
from pages.wue_page import create_wue_page
from pages.home_page import create_home_page
from pages.about_page import create_about_page
from pages.energy_forecast_page import create_forecast_page
from callbacks.chart_callbacks import ChartCallbackManager
from charts.pue_chart import create_pue_scatter_plot
from charts.wue_chart import create_wue_scatter_plot
from charts.forecast_chart import create_forecast_scatter_plot

def create_app():
    app = dash.Dash(
        __name__,
        external_stylesheets=[
            'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap',
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css', # Font Awesome CDN
            dbc.themes.BOOTSTRAP
        ],
        suppress_callback_exceptions=True
    )

    # Load data
    pue_df, company_counts, pue_industry_avg = load_pue_data()
    wue_df, wue_company_counts, wue_industry_avg = load_wue_data()
    forecast_df,forecast_avg = load_energyforecast_data()

    # Create data dictionary for charts
    data_dict = {
        'pue-scatter': {
            'df': pue_df,
            'industry_avg': pue_industry_avg
        },
        'wue-scatter': {
            'df': wue_df,
            'industry_avg': wue_industry_avg
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
        elif pathname == '/data_centers_101':
            return create_about_page()
        else:
            return create_home_page()

    # Add custom CSS for dropdowns
    app.index_string = '''
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
            <style>
                /* Simple fix for dropdown menus */
                .dash-dropdown .Select-menu-outer {
                    z-index: 999 !important;
                }
                
                /* Ensure dropdown stays open during scrolling */
                .dash-dropdown-always-open .Select-menu-outer {
                    position: absolute !important;
                    display: block !important;
                    z-index: 1000 !important;
                }
                
                /* Improve dropdown scrolling behavior */
                .dash-dropdown .Select-menu {
                    max-height: 300px !important;
                    overflow-y: auto !important;
                }
                
                /* Prevent dropdown from closing when clicking on options */
                .dash-dropdown .Select-option {
                    pointer-events: auto !important;
                }
            </style>
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
                <script>
                    // Fix for multi-select dropdown behavior
                    document.addEventListener('DOMContentLoaded', function() {
                        // Prevent dropdown from closing when scrolling
                        document.addEventListener('scroll', function(e) {
                            if (e.target.classList && e.target.classList.contains('Select-menu')) {
                                e.stopPropagation();
                            }
                        }, true);
                    });
                </script>
            </footer>
        </body>
    </html>
    '''

    return app

if __name__ == '__main__':
    app = create_app()
    app.run_server(debug=True)