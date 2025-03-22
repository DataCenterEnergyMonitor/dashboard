from dash import Input, Output, callback, no_update, dcc

def create_chart_callback(app, data_dict, chart_config):
    """
    Create a reusable chart callback with common filtering logic.
    
    Args:
        app: Dash app instance
        data_dict: Dictionary containing the dataframe
        chart_config: Dictionary containing:
            - base_id: ID for the filter components
            - chart_id: ID for the chart
            - chart_creator: Function to create the chart
            - filters: List of filter IDs
    """
    @app.callback(
        Output(chart_config['chart_id'], 'figure'),
        [Input('url', 'pathname')] + [
            Input(
                {"type": "filter-dropdown", "base_id": chart_config['base_id'], "filter_id": filter_id},
                "value"
            )
            for filter_id in chart_config['filters']
        ]
    )
    def update_chart(pathname, *filter_values):
        expected_path = f"/{chart_config['base_id']}"
        print(f"\nCallback triggered for {chart_config['base_id']}")
        print(f"Current pathname: {pathname}")
        print(f"Expected path: {expected_path}")
        print(f"Filter values: {filter_values}")
        
        if pathname != expected_path:
            print(f"Path mismatch, returning no_update")
            return no_update
            
        try:
            # Get the correct data from data_dict
            chart_key = f"{chart_config['base_id']}-scatter"
            print(f"Looking for data with key: {chart_key}")
            print(f"Available keys in data_dict: {list(data_dict.keys())}")
            
            df = data_dict[chart_key]['df'].copy()
            print(f"Initial dataframe shape: {df.shape}")
            print(f"Initial columns: {df.columns.tolist()}")
            
            # Apply filters
            filtered_df = df.copy()
            for filter_id, value in zip(chart_config['filters'], filter_values):
                print(f"\nApplying filter {filter_id} with value {value}")
                if value and value != "All":
                    if isinstance(value, list):
                        if value and not ("All" in value):
                            filtered_df = filtered_df[filtered_df[filter_id].isin(value)]
                    else:
                        filtered_df = filtered_df[filtered_df[filter_id] == value]
                print(f"Data shape after filter {filter_id}: {filtered_df.shape}")
            
            print("\nFinal filtered data shape:", filtered_df.shape)
            
            # Create the chart
            print(f"\nCreating chart using {chart_config['chart_creator'].__name__}")
            figure = chart_config['chart_creator'](filtered_df)
            print("Chart created successfully")
            return figure
            
        except Exception as e:
            print(f"Error in update_chart: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return {
                'data': [],
                'layout': {
                    'xaxis': {'visible': True},
                    'yaxis': {'visible': True},
                    'annotations': [{
                        'text': f'Error: {str(e)}',
                        'xref': 'paper',
                        'yref': 'paper',
                        'showarrow': False,
                        'font': {'size': 20}
                    }]
                }
            }

    # Add download callback if download_id is provided
    if 'download_id' in chart_config:
        @app.callback(
            Output(chart_config['download_id'], "data"),
            Input(f"btn-{chart_config['download_id']}", "n_clicks"),
            prevent_initial_call=True
        )
        def download_data(n_clicks):
            if n_clicks is None:
                return no_update
            df = data_dict[f"{chart_config['base_id']}-scatter"]['df']
            return dcc.send_data_frame(df.to_csv, chart_config['filename'])

    return update_chart 