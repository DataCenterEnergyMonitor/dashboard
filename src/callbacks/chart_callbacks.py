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

class ChartCallbackManager:
    def __init__(self, app, data_dict, chart_configs):
        self.app = app
        self.data_dict = data_dict
        self.chart_configs = chart_configs
        self._register_callbacks()

    def _register_callbacks(self):
        for chart_type, config in self.chart_configs.items():
            # Get the base ID for this chart
            base_id = config['base_id']
            chart_id = config['chart_id']
            
            # Define inputs based on available filters
            inputs = [
                Input({"type": "filter-dropdown", "base_id": base_id, "filter_id": "facility_scope"}, "value"),
                Input({"type": "filter-dropdown", "base_id": base_id, "filter_id": "company"}, "value")
            ]
            
            # Only add geographical_scope input for PUE chart
            if chart_type == 'pue_scatter':
                inputs.append(Input({"type": "filter-dropdown", "base_id": base_id, "filter_id": "geographical_scope"}, "value"))
                inputs.append(Input({"type": "filter-dropdown", "base_id": base_id, "filter_id": "pue_measurement_level"}, "value"))

            # Create a closure to capture the chart_type
            def create_callback(chart_type=chart_type, config=config):
                @self.app.callback(
                    Output(config['chart_id'], 'figure'),
                    inputs,
                    prevent_initial_call=False
                )
                def update_chart(*args):
                    # Parse inputs based on chart type
                    facility_scope = args[0]
                    companies = args[1]
                    
                    # Get the data for this chart
                    df = self.data_dict[chart_type]['df'].copy()
                    industry_avg = self.data_dict[chart_type]['industry_avg']
                    
                    # Apply filters
                    if facility_scope:
                        df = df[df['facility_scope'] == facility_scope]
                    if companies and "All" not in companies:
                        df = df[df['company'].isin(companies)]
                    
                    if chart_type == 'pue_scatter':
                        geo_scope = args[2]
                        measurement_level = args[3]
                        if geo_scope and "All" not in geo_scope:
                            df = df[df['geographical_scope'].isin(geo_scope)]
                        if measurement_level and "All" not in measurement_level:
                            df = df[df['pue_measurement_level'].isin(measurement_level)]
                    
                    # Create the chart using the appropriate creator function
                    return config['chart_creator'](df, facility_scope, industry_avg)

                return update_chart

            # Create and register the callback
            create_callback()

            # Register download callback
            def create_download_callback(chart_type=chart_type, config=config):
                @self.app.callback(
                    Output(config['download_data_id'], "data"),
                    Input(config['download_button_id'], "n_clicks"),
                    prevent_initial_call=True
                )
                def download_data(n_clicks):
                    if n_clicks is None:
                        return dash.no_update
                        
                    df = self.data_dict[chart_type]['df']
                    return dcc.send_data_frame(df.to_csv, config['filename'], index=False)
                
                return download_data

            # Create and register the download callback
            create_download_callback()