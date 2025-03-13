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
            
            # Define inputs based on the specific chart type
            inputs = [
                Input(
                    {"type": "filter-dropdown", "base_id": base_id, "filter_id": filter_id},
                    "value"
                )
                for filter_id in self._get_filter_ids_for_chart(chart_type)
            ]

            # Single callback for both charts
            @self.app.callback(
                [Output(chart_id, 'figure'),
                 Output('timeline-chart', 'src', allow_duplicate=True)],
                inputs,
                prevent_initial_call='initial_duplicate'
            )
            def update_charts(*args, chart_type=chart_type, config=config):
                print(f"Chart update triggered for {chart_type}")
                
                # Get the data for this chart type
                df = self.data_dict[chart_type]['df'].copy()
                
                # Create filter_values dictionary
                filter_ids = self._get_filter_ids_for_chart(chart_type)
                filter_values = dict(zip(filter_ids, args))
                
                # Apply filters
                filtered_df = self._apply_filters(df, filter_values)
                
                if filtered_df.empty:
                    empty_fig = {
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
                    return empty_fig, None

                try:
                    # Create bar chart
                    bar_chart = config['chart_creator'](filtered_df)
                    
                    # Create timeline chart
                    timeline_img = create_timeline_chart(filtered_df)

                    return bar_chart, timeline_img
                except Exception as e:
                    print(f"Error creating chart: {e}")
                    error_fig = {
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
                    return error_fig, None

            # Register download callback
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
        if chart_type == 'reporting-bar':
            return ['year_range_from', 'year_range_to']
        return self.chart_configs[chart_type]['filters']

    def _apply_filters(self, df, filter_values):
        """Apply filters to the dataframe"""
        filtered_df = df.copy()
        
        for filter_id, value in filter_values.items():
            if not value:
                continue
                
            if '_from' in filter_id or '_to' in filter_id:
                # Handle year range filter
                base_id = filter_id.rsplit('_', 1)[0]
                if f"{base_id}_from" in filter_values and f"{base_id}_to" in filter_values:
                    from_year = filter_values[f"{base_id}_from"]
                    to_year = filter_values[f"{base_id}_to"]
                    if from_year and to_year:
                        filtered_df = filtered_df[
                            (filtered_df['reported_data_year'] >= from_year) &
                            (filtered_df['reported_data_year'] <= to_year)
                        ]
            else:
                # Handle regular filters (for scatter plots)
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
  