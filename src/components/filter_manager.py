from dataclasses import dataclass
from typing import Any, Dict, List, Optional, ClassVar
from dash import Dash, dcc, html, Input, Output, callback, no_update
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
    depends_on: List[str] = None  # New field to specify filter dependencies

    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []

class FilterManager:
    # Class variable to track registered callbacks
    _callbacks_registered: ClassVar[bool] = False
    _instances: ClassVar[Dict[str, 'FilterManager']] = {}

    def __init__(self, app, base_id: str, df: pd.DataFrame, filters: List[FilterConfig]):
        self.app = app
        self.base_id = base_id
        self.df = df
        self.filters = {f.id: f for f in filters}
        FilterManager._instances[base_id] = self
        
        if not FilterManager._callbacks_registered:
            self._register_global_callbacks()
            FilterManager._callbacks_registered = True

    def _get_filtered_df(self, filter_values: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to dataframe based on current filter values"""
        df = self.df.copy()
        
        # Apply filters in order of dependencies
        ordered_filters = sorted(
            filter_values.keys(),
            key=lambda x: len(self.filters[x].depends_on) if x in self.filters else 0
        )
        
        for filter_id in ordered_filters:
            value = filter_values[filter_id]
            if value and filter_id in self.filters:
                column = self.filters[filter_id].column
                if isinstance(value, list):
                    if value and "All" not in value:
                        df = df[df[column].isin(value)]
                else:
                    if value != "All":
                        df = df[df[column] == value]
        
        return df

    def _get_filter_options(self, filter_config: FilterConfig, filtered_df: pd.DataFrame) -> List[Dict]:
        """Get options for a specific filter based on filtered dataframe"""
        values = sorted(filtered_df[filter_config.column].dropna().unique())
        options = []
        
        if filter_config.show_all and filter_config.multi:
            options.append({"label": "All", "value": "All"})
            
        options.extend([{"label": str(val), "value": val} for val in values])
        return options

    @classmethod
    def _register_global_callbacks(cls):
        app = next(iter(cls._instances.values())).app

        # Create outputs for all possible filters
        all_filter_ids = set()
        for instance in cls._instances.values():
            all_filter_ids.update(instance.filters.keys())

        outputs = [
            Output(
                {"type": "filter-dropdown", "base_id": dash.ALL, "filter_id": filter_id},
                "options",
                allow_duplicate=True
            )
            for filter_id in all_filter_ids
        ]

        inputs = [
            Input(
                {"type": "filter-dropdown", "base_id": dash.ALL, "filter_id": filter_id},
                "value"
            )
            for filter_id in all_filter_ids
        ]

        @app.callback(
            outputs,
            inputs,
            prevent_initial_call='initial_duplicate'
        )
        def update_filter_options(*input_values):
            ctx = dash.callback_context
            if not ctx.triggered:
                return [[dash.no_update]] * len(outputs)

            # Get the triggered input's properties
            triggered = ctx.triggered[0]
            triggered_prop_id = triggered['prop_id']
            triggered_value = triggered['value']

            try:
                triggered_id = eval(triggered_prop_id.split('.')[0])
                base_id = triggered_id['base_id']
                triggered_filter = triggered_id['filter_id']
            except:
                print(f"Error parsing triggered_prop_id: {triggered_prop_id}")
                return [[dash.no_update]] * len(outputs)

            instance = cls._instances.get(base_id)
            if not instance:
                print(f"No instance found for base_id: {base_id}")
                return [[dash.no_update]] * len(outputs)

            # Get all current filter values from the inputs
            current_values = {}
            input_dict = dict(zip(all_filter_ids, input_values))
            
            # Process filters in order of dependencies
            ordered_filters = sorted(
                instance.filters.keys(),
                key=lambda x: len(instance.filters[x].depends_on)
            )
            
            for filter_id in ordered_filters:
                value = input_dict.get(filter_id)
                if value is not None:
                    if isinstance(value, list):
                        # Handle the case where value is a list of lists (for ALL outputs)
                        instance_value = value[0] if isinstance(value, list) and value else None
                        if instance_value and "All" not in instance_value:
                            current_values[filter_id] = instance_value
                    else:
                        if value != "All":
                            current_values[filter_id] = value

            # Update current values with the triggered value
            if triggered_value is not None:
                if isinstance(triggered_value, list):
                    if triggered_value and "All" not in triggered_value:
                        current_values[triggered_filter] = triggered_value
                    else:
                        current_values.pop(triggered_filter, None)
                elif triggered_value != "All":
                    current_values[triggered_filter] = triggered_value
                else:
                    current_values.pop(triggered_filter, None)

            # Get filtered dataframe based on current values
            filtered_df = instance._get_filtered_df(current_values)

            # Prepare results for each output
            results = []
            for filter_id in all_filter_ids:
                if filter_id in instance.filters:
                    filter_config = instance.filters[filter_id]
                    # Update options for dependent filters
                    if (filter_id == triggered_filter or  # Always update the triggered filter
                        (filter_config.depends_on and triggered_filter in filter_config.depends_on)):
                        options = instance._get_filter_options(filter_config, filtered_df)
                        results.append([options])
                    else:
                        results.append([dash.no_update])
                else:
                    results.append([dash.no_update])

            return results

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
                html.Div(filter_components),  # Keep filters stacked
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