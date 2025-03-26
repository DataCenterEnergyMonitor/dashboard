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
    type: str = "dropdown"  # Can be "dropdown" or "year_range_pair"
    multi: bool = False
    default_value: Any = None
    show_all: bool = True
    depends_on: List[str] = None
    options: Dict[str, Any] = None  # For additional filter-specific options
    component: Optional[Any] = None  # Add this parameter

    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []
        if self.options is None:
            self.options = {}

class FilterManager:
    _registered_callbacks = set()  # Track registered callbacks

    def __init__(self, app, base_id: str, df: pd.DataFrame, filters: List[FilterConfig]):
        print(f"\nInitializing FilterManager for {base_id}")
        self.app = app
        self.base_id = base_id
        self.df = df
        self.filters = {f.id: f for f in filters}
        print(f"Filter configs: {[f.id for f in filters]}")
        self._register_callbacks()

    def _register_callbacks(self):
        """Register callbacks for this specific filter manager instance"""
        callback_key = f"filter_manager_{self.base_id}"
        if callback_key in self._registered_callbacks:
            return
        
        outputs = []
        value_inputs = []
        
        # Create outputs and inputs based on filter type
        for filter_id, filter_config in self.filters.items():
            if filter_config.type == "dropdown":
                outputs.append(
                    Output(
                        {"type": "filter-dropdown", "base_id": self.base_id, "filter_id": filter_id},
                        "options"
                    )
                )
                value_inputs.append(
                    Input(
                        {"type": "filter-dropdown", "base_id": self.base_id, "filter_id": filter_id},
                        "value"
                    )
                )
            elif filter_config.type == "radio":
                # Radio buttons don't need dynamic options
                value_inputs.append(
                    Input(
                        {"type": "filter-radio", "base_id": self.base_id, "filter_id": filter_id},
                        "value"
                    )
                )
        
        if not outputs:  # If no dropdowns, no need to register callback
            return
        
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

            # Process each dropdown filter
            results = []
            for filter_id, filter_config in self.filters.items():
                if filter_config.type != "dropdown":
                    continue
                
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
        
        if filter_config.id == 'reported_data_year':
            # Sort years in descending order
            options = [{'label': str(val), 'value': str(val)} 
                      for val in sorted(unique_values, reverse=True)]
        else:
            options = [{'label': str(val), 'value': str(val)} 
                      for val in sorted(unique_values)]
        
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
        print(f"\nCreating filter components for {self.base_id}")
        filter_components = []
        
        # Create filter components for all filters
        if self.filters:
            for filter_config in self.filters.values():
                if filter_config.type == "dropdown":
                    filter_components.append(self._create_dropdown(filter_config))
                elif filter_config.type == "radio":  # Add radio button handling
                    filter_components.append(self._create_radio(filter_config))
                elif filter_config.type == "year_range_pair":
                    filter_components.append(self._create_year_range_pair(filter_config))

        return html.Div(filter_components)

    def _create_dropdown(self, config: FilterConfig) -> html.Div:
        """Create a dropdown filter component"""
        options = self._get_filter_options(config, self.df)
        
        if config.type == "year_range_pair":
            years = sorted(self.df[config.column].unique())
            min_year, max_year = min(years), max(years)
            
            return html.Div([
                html.Label(
                    config.label,
                    style={'fontFamily': 'Inter', 'fontWeight': '500'}
                ),
                html.Div([
                    # From Year dropdown
                    html.Div([
                        dcc.Dropdown(
                            id={
                                "type": "filter-dropdown",
                                "base_id": self.base_id,
                                "filter_id": f"{config.id}_from"
                            },
                            options=[{'label': str(year), 'value': year} for year in years],
                            value=config.default_value.get('from', min_year),
                            placeholder="From",
                            style={'fontFamily': 'Inter'},
                            clearable=False
                        ),
                    ], style={'width': '48%'}),
                    
                    # To Year dropdown
                    html.Div([
                        dcc.Dropdown(
                            id={
                                "type": "filter-dropdown",
                                "base_id": self.base_id,
                                "filter_id": f"{config.id}_to"
                            },
                            options=[{'label': str(year), 'value': year} for year in years],
                            value=config.default_value.get('to', max_year),
                            placeholder="To",
                            style={'fontFamily': 'Inter'},
                            clearable=False
                        ),
                    ], style={'width': '48%'})
                ], style={
                    'display': 'flex',
                    'justifyContent': 'space-between',
                    'alignItems': 'center',
                    'width': '100%',
                    'marginTop': '5px'
                })
            ], style={
                "marginBottom": "20px",
                "width": "100%",
                "position": "relative",
                "zIndex": "auto"
            })
        
        # Regular dropdown
        return html.Div([
            html.Label(
                config.label,
                style={'fontFamily': 'Inter', 'fontWeight': '500'}
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
                style={
                    'fontFamily': 'Inter'
                },
                clearable=False if not config.multi else True,
                persistence=True,
                persistence_type='session',
                maxHeight=300,
                optionHeight=35,
                className='dash-dropdown'
            ),
        ], style={
            "marginBottom": "20px",
            "width": "100%",
            "position": "relative",
            "zIndex": "auto"
        })

    def _create_year_range_pair(self, config: FilterConfig) -> html.Div:
        """Create a pair of year dropdown filters"""
        years = sorted(self.df[config.column].unique())
        min_year, max_year = min(years), max(years)
        
        # Create the container div
        return html.Div([
            html.Label(
                config.label,
                style={'fontFamily': 'Inter', 'fontWeight': '500'}
            ),
            html.Div([
                # From Year dropdown
                html.Div([
                    dcc.Dropdown(
                        id={
                            "type": "filter-dropdown",
                            "base_id": self.base_id,
                            "filter_id": "from_year"
                        },
                        options=[{'label': str(year), 'value': year} for year in years],
                        value=config.default_value.get('from', min_year),
                        placeholder="From Year",
                        style={'fontFamily': 'Inter'},
                        clearable=False
                    ),
                ], style={'width': '48%'}),
                
                # To Year dropdown
                html.Div([
                    dcc.Dropdown(
                        id={
                            "type": "filter-dropdown",
                            "base_id": self.base_id,
                            "filter_id": "to_year"
                        },
                        options=[{'label': str(year), 'value': year} for year in years],
                        value=config.default_value.get('to', max_year),
                        placeholder="To Year",
                        style={'fontFamily': 'Inter'},
                        clearable=False
                    ),
                ], style={'width': '48%'})
            ], style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'center',
                'width': '100%',
                'marginTop': '5px'
            })
        ], style={
            "marginBottom": "20px",
            "width": "100%",
            "position": "relative",
            "zIndex": "auto"
        })

    def _create_radio(self, config: FilterConfig) -> html.Div:
        """Create a radio button filter component"""
        return html.Div([
            html.Label(
                config.label,
                style={'fontFamily': 'Inter', 'fontWeight': '500'}
            ),
            dcc.RadioItems(
                id={
                    "type": "filter-radio",  # Match the callback Input type
                    "base_id": self.base_id,
                    "filter_id": config.id
                },
                options=config.options["options"],
                value=config.default_value,
                style=config.options.get("style", {}),
                labelStyle=config.options.get("labelStyle", {}),
                inputStyle=config.options.get("inputStyle", {}),
                className=config.options.get("className", "")
            )
        ], style={
            "marginBottom": "20px",
            "width": "100%"
        })