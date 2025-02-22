import dash
from dash.dependencies import Output, Input
from dash import callback_context, no_update
from dash import dcc
from typing import List

class ChartCallbackManager:
    _registered_callbacks = set()  # Track registered callbacks

    def __init__(self, app, data_dict, chart_configs):
        self.app = app
        self.data_dict = data_dict
        self.chart_configs = chart_configs
        self._register_callbacks()

    def _register_callbacks(self):
        for chart_type, config in self.chart_configs.items():
            callback_key = f"chart_{config['base_id']}"
            if callback_key in self._registered_callbacks:
                continue

            base_id = config['base_id']
            chart_id = config['chart_id']
            
            # Define inputs based on the specific chart type
            inputs = [
                Input(
                    {"type": "filter-dropdown", "base_id": base_id, "filter_id": filter_id},
                    "value"
                )
                for filter_id in self._get_filter_ids_for_chart(chart_type)
            ]

            @self.app.callback(
                Output(chart_id, 'figure'),
                inputs,
                prevent_initial_call=False
            )
            def update_chart(*args, chart_type=chart_type, config=config):
                ctx = dash.callback_context
                
                # Get the data for this chart type
                df = self.data_dict[chart_type]['df'].copy()
                industry_avg = self.data_dict[chart_type].get('industry_avg')
                
                # Get filter IDs and values
                filter_ids = self._get_filter_ids_for_chart(chart_type)
                filter_values = dict(zip(filter_ids, args))

                # Apply filters
                filtered_df = df.copy()
                for filter_id, value in filter_values.items():
                    if value:
                        if isinstance(value, list):
                            if value and "All" not in value:
                                filtered_df = filtered_df[filtered_df[filter_id].isin(value)]
                        elif value != "All":
                            filtered_df = filtered_df[filtered_df[filter_id] == value]

                if filtered_df.empty:
                    return {
                        'data': [],
                        'layout': {
                            'xaxis': {'visible': False},
                            'yaxis': {'visible': False},
                            'annotations': [{
                                'text': 'No data available for the selected filters',
                                'xref': 'paper',
                                'yref': 'paper',
                                'showarrow': False,
                                'font': {'size': 20}
                            }]
                        }
                    }

                try:
                    return config['chart_creator'](
                        filtered_df=filtered_df,
                        selected_scope=filter_values.get('facility_scope'),
                        industry_avg=industry_avg
                    )
                except Exception as e:
                    print(f"Error creating chart: {e}")
                    return {
                        'data': [],
                        'layout': {
                            'xaxis': {'visible': False},
                            'yaxis': {'visible': False},
                            'annotations': [{
                                'text': f'Error creating chart: {str(e)}',
                                'xref': 'paper',
                                'yref': 'paper',
                                'showarrow': False,
                                'font': {'size': 20}
                            }]
                        }
                    }

            # Simplified download callback for unfiltered data
            @self.app.callback(
                Output(f"{config['base_id']}-download-data", "data"),
                Input(f"{config['base_id']}-download-button", "n_clicks"),
                prevent_initial_call=True
            )
            def download_data(n_clicks, chart_type=chart_type, config=config):
                if not n_clicks:
                    return dash.no_update
                
                # Get the complete dataset
                df = self.data_dict[chart_type]['df']
                    
                return dcc.send_data_frame(
                    df.to_csv, 
                    filename=config['filename'],
                    index=False
                )

            self._registered_callbacks.add(callback_key)

    def _get_filter_ids_for_chart(self, chart_type: str) -> List[str]:
        """Return the filter IDs needed for each chart type"""
        return self.chart_configs[chart_type]['filters']

    def _apply_filters(self, df, filter_values):
        """Apply filters to the dataframe"""
        filtered_df = df.copy()
        
        # Map filter IDs to DataFrame column names
        column_mapping = {
            'facility_scope': 'facility_scope',
            'company': 'company',
            'iea_region': 'iea_region',
            'iecc_climate_zone_s_' : 'iecc_climate_zone_s_',
            #'geographical_scope': 'geographical_scope',
            'pue_measurement_level': 'pue_measurement_level'
        }

        for filter_id, value in filter_values.items():
            if value and filter_id in column_mapping:
                column = column_mapping[filter_id]
                if isinstance(value, list):
                    if value and "All" not in value:
                        filtered_df = filtered_df[filtered_df[column].isin(value)]
                elif value != "All":
                    filtered_df = filtered_df[filtered_df[column] == value]
        
        return filtered_df