import dash
from dash.dependencies import Output, Input, State
from dash import callback, Input, Output, ALL, MATCH, callback_context, no_update
from dash import dcc
from typing import List
from charts.timeline_chart import create_timeline_chart

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
            
            if base_id == 'reporting':
                @self.app.callback(
                    [Output('reporting-bar-chart', 'figure'),
                     Output('timeline-chart', 'figure')],
                    [Input('url', 'pathname'),
                     Input({"type": "filter-dropdown", "base_id": "reporting", "filter_id": "from_year"}, "value"),
                     Input({"type": "filter-dropdown", "base_id": "reporting", "filter_id": "to_year"}, "value")]
                )
                def update_reporting_charts(pathname, year_from, year_to):
                    if pathname != '/reporting':
                        return dash.no_update, dash.no_update
                    
                    df = self.data_dict['reporting-bar']['df'].copy()
                    
                    # Ensure we have valid year values
                    if year_from is None or year_to is None:
                        return dash.no_update, dash.no_update
                        
                    # Create filter values dict
                    filter_values = {
                        'year_range': {
                            'from': int(year_from),
                            'to': int(year_to)
                        }
                    }
                    
                    try:
                        filtered_df = self._apply_filters(df, filter_values)
                        bar_chart = self.chart_configs['reporting-bar']['chart_creator'](filtered_df)
                        timeline_chart = create_timeline_chart(filtered_df)
                        return bar_chart, timeline_chart
                    except Exception as e:
                        print(f"Error creating charts: {e}")
                        return dash.no_update, dash.no_update
            else:
                @self.app.callback(
                    Output(chart_id, 'figure'),
                    [Input('url', 'pathname')] + [
                        Input(
                            {"type": "filter-dropdown", "base_id": base_id, "filter_id": filter_id},
                            "value"
                        )
                        for filter_id in config['filters']  # Use config's filters directly
                    ]
                )
                def update_chart(pathname, *args, chart_type=chart_type, config=config):
                    print(f"Update chart callback for {chart_type}")
                    expected_pathname = f'/{chart_type.split("-")[0]}'  # Handle 'pue-scatter' -> '/pue'
                    if pathname != expected_pathname:
                        return dash.no_update
                    
                    df = self.data_dict[chart_type]['df'].copy()
                    print(f"Initial {chart_type} dataframe shape: {df.shape}")
                    
                    filter_ids = config['filters']
                    filter_values = dict(zip(filter_ids, args))
                    print(f"Filter values for {chart_type}: {filter_values}")
                    
                    filtered_df = self._apply_filters(df, filter_values)
                    print(f"Filtered {chart_type} dataframe shape: {filtered_df.shape}")
                    
                    try:
                        figure = config['chart_creator'](filtered_df)
                        print(f"Chart created successfully for {chart_type}")
                        return figure
                    except Exception as e:
                        print(f"Error creating {chart_type} chart: {e}")
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

            self._registered_callbacks.add(callback_key)

    def _get_filter_ids_for_chart(self, chart_type: str) -> List[str]:
        """Return the filter IDs needed for each chart type"""
        return self.chart_configs[chart_type].get('filters', [])

    def _apply_filters(self, df, filter_values):
        """Apply filters to the dataframe"""
        filtered_df = df.copy()
        
        for filter_id, value in filter_values.items():
            if value is None or value == []:
                continue

            if filter_id == 'year_range':
                try:
                    if not value:
                        continue
                        
                    from_year = int(value.get('from', min(df['reported_data_year'])))
                    to_year = int(value.get('to', max(df['reported_data_year'])))
                    
                    print(f"Applying year filter: {from_year} to {to_year}")
                    
                    filtered_df = filtered_df[
                        (filtered_df['reported_data_year'] >= from_year) &
                        (filtered_df['reported_data_year'] <= to_year)
                    ]
                except (ValueError, TypeError, AttributeError) as e:
                    print(f"Error processing year range: {e}")
            else:
                if isinstance(value, list):
                    if value and "All" not in value:
                        filtered_df = filtered_df[filtered_df[filter_id].isin(value)]
                elif value != "All":
                    filtered_df = filtered_df[filtered_df[filter_id] == value]
        
        return filtered_df

# Remove this callback as it's causing the conflict
# @callback(
#     Output('reporting-bar-chart', 'figure'),
#     [Input('url', 'pathname'),
#      Input({'type': 'filter-dropdown', 'base_id': 'reporting', 'filter_id': ALL}, 'value')]
# )
# def update_reporting_chart(pathname, filter_values):
#     """Update the reporting bar chart"""
#     if pathname != '/reporting':
#         return dash.no_update
# 
#     # Create the bar chart with the full dataset since we have no filters
#     return create_reporting_bar_plot(reporting_df)
  