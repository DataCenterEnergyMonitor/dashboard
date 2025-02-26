from dataclasses import dataclass
from typing import Any, Dict, List, Optional, ClassVar
from dash import Dash, dcc, html, Input, Output, callback, no_update, State
import pandas as pd
import dash

@dataclass
class FilterConfig:
    id: str
    label: str
    column: str
    type: str = "dropdown"
    multi: bool = False
    default_value: Any = None
    show_all: bool = True
    depends_on: List[str] = None

    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []

class FilterManager:
    _registered_callbacks = set()  # Track registered callbacks

    def __init__(self, app, base_id: str, df: pd.DataFrame, filters: List[FilterConfig]):
        self.app = app
        self.base_id = base_id
        self.df = df
        self.filters = {f.id: f for f in filters}
        self._register_callbacks()

    def _register_callbacks(self):
        """Register callbacks for this specific filter manager instance"""
        callback_key = f"filter_manager_{self.base_id}"
        if callback_key in self._registered_callbacks:
            return
        
        outputs = [
            Output(
                {"type": "filter-dropdown", "base_id": self.base_id, "filter_id": filter_id},
                "options"
            )
            for filter_id in self.filters.keys()
        ]

        # Value inputs
        value_inputs = [
            Input(
                {"type": "filter-dropdown", "base_id": self.base_id, "filter_id": filter_id},
                "value"
            )
            for filter_id in self.filters.keys()
        ]

        @self.app.callback(
            outputs,
            value_inputs,
            prevent_initial_call=False
        )
        def update_filter_options(*input_values):
            ctx = dash.callback_context
            
            # Get current values
            current_values = {}
            for filter_id, value in zip(self.filters.keys(), input_values):
                filter_config = self.filters[filter_id]
                if value is not None:
                    current_values[filter_id] = value
                elif not ctx.triggered and filter_config.default_value is not None:
                    current_values[filter_id] = filter_config.default_value

            # Get triggered filter
            triggered_filter = None
            if ctx.triggered:
                triggered_id = eval(ctx.triggered[0]['prop_id'].split('.')[0])
                triggered_filter = triggered_id.get('filter_id')

            # Process each filter
            results = []
            for filter_id in self.filters.keys():
                filter_config = self.filters[filter_id]
                
                # If it's initial load and filter has a default value, don't update options
                if not ctx.triggered and filter_config.default_value is not None:
                    results.append(dash.no_update)
                    continue

                # Always update dependent filters when their parent changes
                should_update = (
                    triggered_filter is None or  # Initial load
                    filter_id == triggered_filter or  # This filter was triggered
                    (filter_config.depends_on and triggered_filter in filter_config.depends_on)  # Dependency changed
                )

                if not should_update:
                    results.append(dash.no_update)
                    continue

                # Apply filters based on dependencies
                filtered_df = self.df.copy()
                if filter_config.depends_on:
                    for dep_filter in filter_config.depends_on:
                        if dep_filter in current_values and current_values[dep_filter]:
                            dep_value = current_values[dep_filter]
                            if isinstance(dep_value, list):
                                if "All" not in dep_value:
                                    filtered_df = filtered_df[filtered_df[self.filters[dep_filter].column].isin(dep_value)]
                            elif dep_value != "All":
                                filtered_df = filtered_df[filtered_df[self.filters[dep_filter].column] == dep_value]

                # Get new options while preserving current values
                options = self._get_filter_options(filter_config, filtered_df)
                
                # If this is a multi-select filter and has current values, ensure they're in options
                if filter_config.multi and filter_id in current_values:
                    current_vals = current_values[filter_id]
                    if isinstance(current_vals, list):
                        existing_values = {opt['value'] for opt in options}
                        for val in current_vals:
                            if val not in existing_values and val != "All":
                                options.append({'label': str(val), 'value': str(val)})
                
                results.append(options)

            return results

        self._registered_callbacks.add(callback_key)

    def _get_filter_options(self, filter_config: FilterConfig, filtered_df: pd.DataFrame) -> List[Dict]:
        """Get options for a filter based on the filtered dataframe"""
        unique_values = filtered_df[filter_config.column].dropna().unique()
        options = [{'label': str(val), 'value': str(val)} for val in sorted(unique_values)]
        
        if filter_config.show_all and len(options) > 1:
            options.insert(0, {'label': 'All', 'value': 'All'})
            
        return options

    def _get_filtered_df(self, filter_values: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to dataframe based on current filter values"""
        df = self.df.copy()
        
        for filter_id, value in filter_values.items():
            if value and filter_id in self.filters:
                column = self.filters[filter_id].column
                if isinstance(value, list):
                    if value and "All" not in value:
                        df = df[df[column].isin(value)]
                elif value != "All":
                    df = df[df[column] == value]
        
        return df

    def create_filter_components(self) -> html.Div:
        """Create all filter components"""
        filter_components = []
        
        # Create filter dropdowns
        for filter_config in self.filters.values():
            if filter_config.type == "dropdown":
                filter_components.append(self._create_dropdown(filter_config))
        
        # Add download button
        download_button = html.Button(
            "Download Data",
            id=f"{self.base_id}-download-button",
            style={
                'backgroundColor': '#4CAF50',
                'color': 'white',
                'padding': '12px 24px',
                'border': 'none',
                'borderRadius': '4px',
                'cursor': 'pointer',
                'fontFamily': 'Roboto',
                'fontWeight': '500',
                'fontSize': '14px',
                'width': '200px'
            }
        )

        # Download component
        download_component = dcc.Download(id=f"{self.base_id}-download-data")

        return html.Div(
            [
                html.Div(filter_components),
                html.Div(
                    [download_button, download_component],
                    style={
                        "display": "flex",
                        "justifyContent": "flex-end",
                        "marginBottom": "20px"
                    }
                )
            ]
        )

    def _create_dropdown(self, config: FilterConfig) -> html.Div:
        """Create a dropdown filter component"""
        options = self._get_filter_options(config, self.df)
        
        return html.Div([
            html.Label(
                config.label,
                style={'fontFamily': 'Roboto', 'fontWeight': '500'}
            ),
            dcc.Dropdown(
                id={
                    "type": "filter-dropdown",
                    "base_id": self.base_id,
                    "filter_id": config.id
                },
                options=options,
                value=config.default_value,
                multi=config.multi,
                placeholder=f"Select {config.label}",
                style={'fontFamily': 'Roboto'},
                clearable=False if not config.multi else True
            ),
        ], style={"marginBottom": "20px", "width": "100%"})