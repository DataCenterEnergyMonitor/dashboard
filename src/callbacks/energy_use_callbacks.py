from dash import Input, Output, callback, no_update, dcc
import dash
import traceback
import pandas as pd
from dash.exceptions import PreventUpdate

# Add this at the top of the file
_energy_use_callback_registered = False

def create_energy_use_callback(app, data_dict, chart_configs):
    """Create a specialized callback for energy use chart with its own filters"""
    print("Registering energy use callback")
    
    # Create the chart configuration if it doesn't exist
    if 'energy-use-bar' not in chart_configs:
        from figures.company_profile.energy_use_barchart import create_energy_use_bar_plot
        chart_configs['energy-use-bar'] = {
            'chart_creator': create_energy_use_bar_plot,
            'df': data_dict['energy-use-bar']['df']
        }
    
    @app.callback(
        Output('energy-use-bar-chart', 'figure'),
        [
            Input('url', 'pathname'),
            Input(
                {"type": "filter-dropdown", "base_id": "energy-use", "filter_id": "reported_data_year"},
                "value"
            ),
            Input(
                {"type": "filter-radio", "base_id": "energy-use", "filter_id": "reporting_scope"},
                "value"
            ),
            Input(
                {"type": "filter-dropdown", "base_id": "energy-use", "filter_id": "company_name"},
                "value"
            )
        ]
    )
    def update_energy_use_chart(pathname, year, scope, companies):
        if pathname != '/energy-use':
            raise PreventUpdate
            
        print(f"Updating chart with filters: year={year}, scope={scope}, companies={companies}")
        
        try:
            df = data_dict['energy-use-bar']['df'].copy()
            
            # Apply filters
            if year:
                df = df[df['reported_data_year'] == int(year)]
            
            if scope and scope != "All":
                df = df[df['reporting_scope'] == scope]
            
            if companies and "All" not in companies:
                df = df[df['company_name'].isin(companies)]
            
            # Ensure we have data after filtering
            if df.empty:
                print("No data after applying filters")
                return create_empty_chart("No data available for selected filters")
            
            figure = create_energy_use_bar_plot(df)
            return figure
            
        except Exception as e:
            print(f"Error updating energy use chart: {str(e)}")
            traceback.print_exc()
            return create_empty_chart(f"Error creating chart: {str(e)}")

    # Register download callback
    @app.callback(
        Output("download-dataframe-csv", "data"),
        Input("btn-download", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_data(n_clicks):
        if n_clicks is None:
            return PreventUpdate
            
        df = data_dict['energy-use-bar']['df'].copy()
        return dcc.send_data_frame(df.to_csv, "energy_use_data.csv", index=False)

def register_energy_use_callbacks(app, data_dict, chart_configs):
    """Register all callbacks related to energy use charts"""
    global _energy_use_callback_registered
    
    print("Attempting to register energy use callbacks...")
    print("Called from:")
    for line in traceback.format_stack()[:-1]:
        print(line.strip())
    
    if _energy_use_callback_registered:
        print("Energy use callbacks already registered, skipping...")
        return
        
    # Register the main chart callback
    create_energy_use_callback(app, data_dict, chart_configs)
    
    ## Register the download callback with updated IDs
    # @app.callback(
    #     Output("download-energy-use-data", "data"),
    #     Input("btn-download-energy-use-data", "n_clicks"),
    #     prevent_initial_call=True
    # )
    # def download_energy_data(n_clicks):
    #     if n_clicks is None:
    #         raise PreventUpdate
            
    #     try:
    #         df = data_dict['energy-use-bar']['df'].copy()
            
    #         # Format the data for download
    #         download_df = df[[
    #             'company_name',
    #             'reporting_scope',
    #             'reported_data_year',
    #             'electricity_usage_kwh'
    #         ]].copy()
            
    #         # Convert electricity usage to billions for readability
    #         download_df['electricity_usage_billion_kwh'] = download_df['electricity_usage_kwh'] / 1e9
            
    #         print(f"Preparing download with {len(download_df)} rows")
            
    #         return dcc.send_data_frame(
    #             download_df.to_csv,
    #             filename="energy-use-data.csv",
    #             index=False
    #         )
            
        # except Exception as e:
        #     print(f"Error in download callback: {str(e)}")
        #     traceback.print_exc()
        #     raise PreventUpdate

    _energy_use_callback_registered = True
    print("Successfully registered energy use callbacks")

def create_empty_chart(message):
    return {
        'data': [],
        'layout': {
            'xaxis': {'visible': False},
            'yaxis': {'visible': False},
            'annotations': [{
                'text': message,
                'xref': 'paper',
                'yref': 'paper',
                'showarrow': False,
                'font': {'size': 20}
            }]
        }
    } 

def create_energy_use_download_callback(app, data_dict):
    """Create download callback for energy-use page"""
    @app.callback(
        Output("download-energy-use-data", "data"),
        Input("btn-download-energy-use-data", "n_clicks"),
        prevent_initial_call=True
    )
    def download_energy_use_data(n_clicks):
        if n_clicks is None:
            return no_update
        df = data_dict['energy-use-bar']['df']
        return dcc.send_data_frame(df.to_csv, "energy-use-data.csv") 