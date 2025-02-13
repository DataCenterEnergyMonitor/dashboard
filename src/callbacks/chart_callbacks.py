# # from dash.dependencies import Output, Input
# # from dash import callback_context, no_update
# # from dash import dcc

# # class ChartCallbackManager:
# #     def __init__(self, app, data_dict, chart_configs):
# #         self.app = app
# #         self.data = data_dict
# #         self.configs = chart_configs
# #         self._register_chart_callbacks()  # Fixed method name

# #     def _register_chart_callbacks(self):  # Fixed method name
# #         """Register callbacks for all chart types"""
# #         for chart_type, config in self.configs.items():
# #             self._register_chart_callback(config)
# #             self._register_download_callback(config)

# #     def _register_chart_callback(self, config):
# #         """Register callback for updating the chart"""
# #         @self.app.callback(
# #             Output(config['chart_id'], 'figure'),
# #             [Input(f"pue-facility_scope-dropdown", 'value'),
# #              Input(f"pue-company-dropdown", 'value'),
# #              Input(f"pue-geographical_scope-dropdown", 'value'),
# #              Input(f"pue-pue_measurement_level-dropdown", 'value')]
# #         )
# #         def update_chart(facility_scope, companies, geographical_scope, measurement_level):
# #             ctx = callback_context
# #             if not ctx.triggered:
# #                 return {}

# #             chart_data = self.data[config['chart_type']]
# #             filtered_df = chart_data['df'].copy()

# #             # Apply filters
# #             if facility_scope:
# #                 filtered_df = filtered_df[filtered_df['facility_scope'] == facility_scope]
            
# #             if companies:
# #                 if isinstance(companies, str):
# #                     companies = [companies]
# #                 if "All" not in companies:
# #                     filtered_df = filtered_df[filtered_df['company'].isin(companies)]
            
# #             if geographical_scope:
# #                 if isinstance(geographical_scope, str):
# #                     geographical_scope = [geographical_scope]
# #                 if "All" not in geographical_scope:
# #                     filtered_df = filtered_df[filtered_df['geographical_scope'].isin(geographical_scope)]
            
# #             if measurement_level:
# #                 if isinstance(measurement_level, str):
# #                     measurement_level = [measurement_level]
# #                 if "All" not in measurement_level:
# #                     filtered_df = filtered_df[filtered_df['pue_measurement_level'].isin(measurement_level)]

# #             if filtered_df.empty:
# #                 return {}

# #             try:
# #                 figure = config['chart_creator'](
# #                     filtered_df=filtered_df,
# #                     selected_scope=facility_scope,
# #                     industry_avg=chart_data.get('industry_avg', None)
# #                 )
# #                 return figure
# #             except Exception as e:
# #                 print(f"Error creating chart: {e}")
# #                 return {}

# #     def _register_download_callback(self, config):
# #         """Register callback for data downloads"""
# #         @self.app.callback(
# #             Output(config['download_data_id'], "data"),
# #             [Input(config['download_button_id'], "n_clicks"),
# #              Input(f"pue-facility_scope-dropdown", 'value'),
# #              Input(f"pue-company-dropdown", 'value'),
# #              Input(f"pue-geographical_scope-dropdown", 'value'),
# #              Input(f"pue-pue_measurement_level-dropdown", 'value')]
# #         )
# #         def download_data(n_clicks, facility_scope, companies, geographical_scope, measurement_level):
# #             if not n_clicks or callback_context.triggered_id != config['download_button_id']:
# #                 return no_update

# #             chart_data = self.data[config['chart_type']]
# #             filtered_df = chart_data['df'].copy()

# #             # Apply filters
# #             if facility_scope:
# #                 filtered_df = filtered_df[filtered_df['facility_scope'] == facility_scope]
            
# #             if companies:
# #                 if isinstance(companies, str):
# #                     companies = [companies]
# #                 if "All" not in companies:
# #                     filtered_df = filtered_df[filtered_df['company'].isin(companies)]
            
# #             if geographical_scope:
# #                 if isinstance(geographical_scope, str):
# #                     geographical_scope = [geographical_scope]
# #                 if "All" not in geographical_scope:
# #                     filtered_df = filtered_df[filtered_df['geographical_scope'].isin(geographical_scope)]
            
# #             if measurement_level:
# #                 if isinstance(measurement_level, str):
# #                     measurement_level = [measurement_level]
# #                 if "All" not in measurement_level:
# #                     filtered_df = filtered_df[filtered_df['pue_measurement_level'].isin(measurement_level)]

# #             return dcc.send_data_frame(filtered_df.to_csv, config['filename'])

# # chart_callbacks.py
# from dash.dependencies import Output, Input
# from dash import callback_context, no_update
# from dash import dcc

# class ChartCallbackManager:
#     def __init__(self, app, data_dict, chart_configs):
#         self.app = app
#         self.data = data_dict
#         self.configs = chart_configs
#         self._register_chart_callbacks()

#     def _register_chart_callbacks(self):
#         """Register callbacks for all chart types"""
#         for chart_type, config in self.configs.items():
#             self._register_chart_callback(config)
#             self._register_download_callback(config)

#     def _register_chart_callback(self, config):
#         """Register callback for updating the chart only"""
#         @self.app.callback(
#             Output(config['chart_id'], 'figure'),
#             [Input(f"{config['base_id']}-facility_scope-dropdown", 'value'),
#              Input(f"{config['base_id']}-company-dropdown", 'value'),
#              Input(f"{config['base_id']}-geographical_scope-dropdown", 'value'),
#              Input(f"{config['base_id']}-pue_measurement_level-dropdown", 'value')]
#         )
#         def update_chart(facility_scope, companies, geographical_scope, measurement_level):
#             ctx = callback_context
#             if not ctx.triggered:
#                 return {}

#             chart_data = self.data[config['chart_type']]
#             filtered_df = chart_data['df'].copy()

#             # Apply filters
#             if facility_scope:
#                 filtered_df = filtered_df[filtered_df['facility_scope'] == facility_scope]
            
#             if companies:
#                 if isinstance(companies, str):
#                     companies = [companies]
#                 if "All" not in companies:
#                     filtered_df = filtered_df[filtered_df['company'].isin(companies)]
            
#             if geographical_scope:
#                 if isinstance(geographical_scope, str):
#                     geographical_scope = [geographical_scope]
#                 if "All" not in geographical_scope:
#                     filtered_df = filtered_df[filtered_df['geographical_scope'].isin(geographical_scope)]
            
#             if measurement_level:
#                 if isinstance(measurement_level, str):
#                     measurement_level = [measurement_level]
#                 if "All" not in measurement_level:
#                     filtered_df = filtered_df[filtered_df['pue_measurement_level'].isin(measurement_level)]

#             if filtered_df.empty:
#                 return {}

#             try:
#                 figure = config['chart_creator'](
#                     filtered_df=filtered_df,
#                     selected_scope=facility_scope,
#                     industry_avg=chart_data.get('industry_avg', None)
#                 )
#                 return figure
#             except Exception as e:
#                 print(f"Error creating chart: {e}")
#                 return {}

#     def _register_download_callback(self, config):
#         """Register callback for data downloads"""
#         @self.app.callback(
#             Output(config['download_data_id'], "data"),
#             [Input(config['download_button_id'], "n_clicks"),
#              Input(f"{config['base_id']}-facility_scope-dropdown", 'value'),
#              Input(f"{config['base_id']}-company-dropdown", 'value'),
#              Input(f"{config['base_id']}-geographical_scope-dropdown", 'value'),
#              Input(f"{config['base_id']}-pue_measurement_level-dropdown", 'value')]
#         )
#         def download_data(n_clicks, facility_scope, companies, geographical_scope, measurement_level):
#             if not n_clicks or callback_context.triggered_id != config['download_button_id']:
#                 return no_update

#             chart_data = self.data[config['chart_type']]
#             filtered_df = chart_data['df'].copy()

#             # Apply filters
#             if facility_scope:
#                 filtered_df = filtered_df[filtered_df['facility_scope'] == facility_scope]
            
#             if companies:
#                 if isinstance(companies, str):
#                     companies = [companies]
#                 if "All" not in companies:
#                     filtered_df = filtered_df[filtered_df['company'].isin(companies)]
            
#             if geographical_scope:
#                 if isinstance(geographical_scope, str):
#                     geographical_scope = [geographical_scope]
#                 if "All" not in geographical_scope:
#                     filtered_df = filtered_df[filtered_df['geographical_scope'].isin(geographical_scope)]
            
#             if measurement_level:
#                 if isinstance(measurement_level, str):
#                     measurement_level = [measurement_level]
#                 if "All" not in measurement_level:
#                     filtered_df = filtered_df[filtered_df['pue_measurement_level'].isin(measurement_level)]

#             return dcc.send_data_frame(filtered_df.to_csv, config['filename'])
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

            # Get the base ID for this chart
            base_id = config['base_id']
            chart_id = config['chart_id']
            
            # Define inputs based on the specific chart type
            inputs = [
                Input({"type": "filter-dropdown", "base_id": base_id, "filter_id": filter_id}, "value")
                for filter_id in self._get_filter_ids_for_chart(chart_type)
            ]

            # Create chart update callback
            @self.app.callback(
                Output(chart_id, 'figure'),
                inputs,
                prevent_initial_call=False
            )
            def update_chart(*args, chart_type=chart_type, config=config):
                ctx = callback_context
                
                # Get the data for this chart type
                df = self.data_dict[chart_type]['df'].copy()
                industry_avg = self.data_dict[chart_type].get('industry_avg')
                
                # Get filter IDs and values
                filter_ids = self._get_filter_ids_for_chart(chart_type)
                filter_values = dict(zip(filter_ids, args))

                # Handle initial load
                if not ctx.triggered:
                    # Apply default filters
                    filtered_df = df.copy()
                    for filter_id, value in filter_values.items():
                        if value is not None:  # Use provided default values
                            if isinstance(value, list):
                                if value and "All" not in value:
                                    filtered_df = filtered_df[filtered_df[filter_id].isin(value)]
                            elif value != "All":
                                filtered_df = filtered_df[filtered_df[filter_id] == value]
                else:
                    # Apply selected filters
                    filtered_df = self._apply_filters(df, filter_values)

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
            'geographical_scope': 'geographical_scope',
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