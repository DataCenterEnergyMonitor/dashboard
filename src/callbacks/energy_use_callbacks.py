from dash import Input, Output, callback, no_update, dcc
import dash
import traceback

# Add this at the top of the file
_energy_use_callback_registered = False

def create_energy_use_callback(app, data_dict, chart_configs):
    """Create a specialized callback for energy use chart with its own filters"""
    print("Registering energy use callback")
    
    # Create the chart configuration if it doesn't exist
    if 'energy-use-bar' not in chart_configs:
        from charts.energy_use_barchart import create_energy_use_bar_plot
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
        ],
        prevent_initial_call=False
    )
    def update_energy_use_chart(pathname, year, scope, companies):
        if pathname != '/energy-use':
            return no_update
        
        try:
            print(f"Updating chart with filters: year={year}, scope={scope}, companies={companies}")
            df = data_dict['energy-use-bar']['df'].copy()
            
            # Apply filters
            if year:
                df = df[df['reported_data_year'] == int(year)]
            
            # Handle scope filter
            if scope and scope != "All":
                df = df[df['reporting_scope'] == scope]
            
            if companies and "All" not in companies:
                df = df[df['company_name'].isin(companies)]
            
            # Use the chart creator function directly
            from charts.energy_use_barchart import create_energy_use_bar_plot
            figure = create_energy_use_bar_plot(df)
            return figure
            
        except Exception as e:
            print(f"Error updating energy use chart: {str(e)}")
            traceback.print_exc()
            return {
                'data': [],
                'layout': {
                    'xaxis': {'visible': True},
                    'yaxis': {'visible': True},
                    'annotations': [{
                        'text': f'Error creating chart: {str(e)}',
                        'xref': 'paper',
                        'yref': 'paper',
                        'showarrow': False,
                        'font': {'size': 20}
                    }]
                }
            }

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
        
    create_energy_use_callback(app, data_dict, chart_configs)
    _energy_use_callback_registered = True
    print("Successfully registered energy use callbacks")

def register_download_callback(app, data_dict):
    @app.callback(
        Output("download-energy-data", "data"),
        Input("btn-download-energy", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_energy_data(n_clicks):
        if n_clicks is None:
            return None
            
        df = data_dict['energy-use-bar']['df'].copy()
        
        # Format the data for download
        download_df = df[[
            'company_name',
            'reporting_scope',
            'reported_data_year',
            'electricity_usage_kwh'
        ]].copy()
        
        # Convert electricity usage to billions for readability
        download_df['electricity_usage_billion_kwh'] = download_df['electricity_usage_kwh'] / 1e9
        
        return dcc.send_data_frame(
            download_df.to_csv,
            "energy_usage_data.csv",
            index=False
        ) 