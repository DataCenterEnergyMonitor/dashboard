import dash
from dash.dependencies import Output, Input, State
from dash import callback, Input, Output, ALL, MATCH, callback_context, no_update
from dash import dcc
from typing import List
#from figures.timeline_chart import create_timeline_bar_plot
#from .reporting_callbacks import register_reporting_callbacks


class ChartCallbackManager:
    _registered_callbacks = set()  # Track registered callbacks

    def __init__(self, app, data_dict, chart_configs):
        self.app = app
        self.data_dict = data_dict
        self.chart_configs = chart_configs
        self._register_callbacks()

    def _register_callbacks(self):
        """Register callbacks for this specific chart manager instance"""
        for chart_type, config in self.chart_configs.items():
            # Exclude charts that have their own specialized callbacks
            if chart_type in [
                "reporting-bar",
                "timeline",
                "energy-use-bar",
                "company-profile-bar",
                "company-profile-table",
            ]:
                continue

            callback_key = f"chart_{config['base_id']}"
            if callback_key in self._registered_callbacks:
                continue

            self._register_chart_callback(chart_type, config)
            self._registered_callbacks.add(callback_key)

    def _register_chart_callback(self, chart_type, config):
        """Register callback for a specific chart type"""
        base_id = config["base_id"]
        chart_id = config["chart_id"]

        @self.app.callback(
            Output(chart_id, "figure"),
            [Input("url", "pathname")]
            + [
                Input(
                    {
                        "type": "filter-dropdown",
                        "base_id": base_id,
                        "filter_id": filter_id,
                    },
                    "value",
                )
                for filter_id in config["filters"]
            ],
        )
        def update_chart(pathname, *args, chart_type=chart_type, config=config):
            print(f"Update chart callback for {chart_type}")
            expected_pathname = (
                f"/{chart_type.split('-')[0]}"  # Handle 'pue-scatter' -> '/pue'
            )
            if pathname != expected_pathname:
                return dash.no_update

            df = self.data_dict[chart_type]["df"].copy()
            print(f"Initial {chart_type} dataframe shape: {df.shape}")

            filter_ids = config["filters"]
            filter_values = dict(zip(filter_ids, args))
            print(f"Filter values for {chart_type}: {filter_values}")

            filtered_df = self._apply_filters(df, filter_values)
            print(f"Filtered {chart_type} dataframe shape: {filtered_df.shape}")

            try:
                figure = config["chart_creator"](filtered_df)
                print(f"Chart created successfully for {chart_type}")
                return figure
            except Exception as e:
                print(f"Error creating {chart_type} chart: {e}")
                return {
                    "data": [],
                    "layout": {
                        "xaxis": {"visible": True},
                        "yaxis": {"visible": True},
                        "annotations": [
                            {
                                "text": f"Error creating chart: {str(e)}",
                                "xref": "paper",
                                "yref": "paper",
                                "showarrow": False,
                                "font": {"size": 20},
                            }
                        ],
                    },
                }

    def _get_filter_ids_for_chart(self, chart_type: str) -> List[str]:
        """Return the filter IDs needed for each chart type"""
        return self.chart_configs[chart_type].get("filters", [])

    def _apply_filters(self, df, filter_values):
        """Apply filters to the dataframe"""
        filtered_df = df.copy()

        for filter_id, value in filter_values.items():
            if value is None or value == []:
                continue

            if filter_id == "year_range":
                try:
                    if not value:
                        continue

                    from_year = int(value.get("from", min(df["reported_data_year"])))
                    to_year = int(value.get("to", max(df["reported_data_year"])))

                    print(f"Applying year filter: {from_year} to {to_year}")

                    filtered_df = filtered_df[
                        (filtered_df["reported_data_year"] >= from_year)
                        & (filtered_df["reported_data_year"] <= to_year)
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
