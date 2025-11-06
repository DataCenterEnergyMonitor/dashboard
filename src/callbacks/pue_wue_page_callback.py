
import dash
from pathlib import Path
from dash import Dash, Input, Output, State, callback, dcc, html, callback_context
import pandas as pd
from charts.pue_chart import create_pue_scatter_plot
from charts.wue_chart import create_wue_scatter_plot
from charts.pue_wue_chart import create_pue_wue_scatter_plot
from components.excel_export import create_filtered_excel_download



def apply_multi_value_filter(df, column, selected_values):
    """Helper function to apply multi-value string matching filter"""
    if not selected_values:
        return df
        
    mask = pd.Series([False] * len(df), index=df.index)
    for value in selected_values:
        mask = mask | df[column].str.contains(value, case=False, na=False, regex=False)
    return df[mask]

def get_multi_value_options(df, column):
    """Extract unique values from multi-value fields"""
    all_values = set()
    for value_str in df[column].dropna().unique():
        values = [v.strip() for v in str(value_str).split(',')]
        all_values.update(values)
    return [{'label': val, 'value': val} for val in sorted(all_values) if val]

def filter_data(df, company_name, time_period_category, measurement_category, metric_type, facility_scope, 
                region, country, state, county, city, assigned_climate_zones, default_climate_zones, cooling_technologies):
    """Filter dataframe based on all selections"""
    filtered_df = df.copy()
    
    # Standard single-value filters
    if company_name: filtered_df = filtered_df[filtered_df['company_name'].isin(company_name)]
    if time_period_category: filtered_df = filtered_df[filtered_df['time_period_category'].isin(time_period_category)]
    if measurement_category: filtered_df = filtered_df[filtered_df['measurement_category'].isin(measurement_category)]
    if metric_type: filtered_df = filtered_df[filtered_df['metric_type'].isin(metric_type)]
    if facility_scope: filtered_df = filtered_df[filtered_df['facility_scope'].isin(facility_scope)]
    
    # Multi-value address fields
    filtered_df = apply_multi_value_filter(filtered_df, 'region', region)
    filtered_df = apply_multi_value_filter(filtered_df, 'country', country)
    filtered_df = apply_multi_value_filter(filtered_df, 'state_province', state)
    filtered_df = apply_multi_value_filter(filtered_df, 'county', county)
    filtered_df = apply_multi_value_filter(filtered_df, 'city', city)
    
    # Multi-value climate and cooling fields
    filtered_df = apply_multi_value_filter(filtered_df, 'assigned_climate_zones', assigned_climate_zones)
    filtered_df = apply_multi_value_filter(filtered_df, 'default_climate_zones', default_climate_zones)
    # TODO: Temporarily disabled - enable when cooling technology options are finalized
    #filtered_df = apply_multi_value_filter(filtered_df, 'assigned_cooling_technologies', cooling_technologies)
    
    return filtered_df


def register_pue_wue_callbacks(app, df):
    # Update all filters
    @app.callback(
        [Output('region', 'options'), Output('country', 'options'), Output('state', 'options'), 
        Output('county', 'options'), Output('city', 'options'), Output('assigned_climate_zones', 'options'), 
        Output('default_climate_zones', 'options'), Output('cooling_technologies', 'options'), Output('climate-section', 'style')],
        [Input('company_name', 'value'), Input('time_period_category', 'value'), Input('measurement_category', 'value'),
        Input('metric_type', 'value'), Input('facility_scope', 'value'), Input('region', 'value'),
        Input('country', 'value'), Input('state', 'value'), Input('county', 'value'),
        Input('city', 'value'), Input('assigned_climate_zones', 'value'), Input('default_climate_zones', 'value'),
        Input('cooling_technologies', 'value')]
    )
    def update_filters(company_name, time_period_category, measurement_category, metric_type, facility_scope,
                    region, country, state, county, city, assigned_climate_zones, default_climate_zone, cooling_technologies):
        
        # Start with full data for each filter's options
        base_df = df.copy()
        
        # Apply company filter first to all subsequent filters
        if company_name: 
            base_df = base_df[base_df['company_name'].isin(company_name)]
        
        # Location filters: depend on company + higher level locations
        region_df = base_df.copy()
        region_opts = get_multi_value_options(region_df, 'region')
        
        country_df = base_df.copy() 
        country_df = apply_multi_value_filter(country_df, 'region', region)
        country_opts = get_multi_value_options(country_df, 'country')
        
        state_df = base_df.copy()
        state_df = apply_multi_value_filter(state_df, 'region', region)
        state_df = apply_multi_value_filter(state_df, 'country', country)
        state_opts = get_multi_value_options(state_df, 'state_province')
        
        county_df = base_df.copy()
        county_df = apply_multi_value_filter(county_df, 'region', region)
        county_df = apply_multi_value_filter(county_df, 'country', country)
        county_df = apply_multi_value_filter(county_df, 'state_province', state)
        county_opts = get_multi_value_options(county_df, 'county')
        
        city_df = base_df.copy()
        city_df = apply_multi_value_filter(city_df, 'region', region)
        city_df = apply_multi_value_filter(city_df, 'country', country)
        city_df = apply_multi_value_filter(city_df, 'state_province', state)
        city_df = apply_multi_value_filter(city_df, 'county', county)
        city_opts = get_multi_value_options(city_df, 'city')
        
        # Climate filters: depend on company and facility scope + all location filters
        climate_df = base_df.copy()
        
        # Apply all location filters to climate data
        climate_df = apply_multi_value_filter(climate_df, 'region', region)
        climate_df = apply_multi_value_filter(climate_df, 'country', country)
        climate_df = apply_multi_value_filter(climate_df, 'state_province', state)
        climate_df = apply_multi_value_filter(climate_df, 'county', county)
        climate_df = apply_multi_value_filter(climate_df, 'city', city)
    
        # Disable climate filters if Fleet-wide is selected
        climate_disabled = facility_scope and 'Fleet-wide' in facility_scope
        if climate_disabled or (facility_scope and 'Single location' not in facility_scope):
            climate_opts = default_opts = cooling_opts = []
        else:
            if facility_scope: climate_df = climate_df[climate_df['facility_scope'].isin(facility_scope)]
            climate_opts = get_multi_value_options(climate_df, 'assigned_climate_zones')
            default_opts = get_multi_value_options(climate_df, 'default_climate_zones')
            cooling_opts = get_multi_value_options(climate_df, 'assigned_cooling_technologies')
        
        # Climate section styling
        climate_style = {
            'opacity': 0.5 if climate_disabled else 1,
            'pointerEvents': 'none' if climate_disabled else 'auto',
            'transition': 'opacity 0.3s ease'
        }
        
        return (region_opts, country_opts, state_opts, county_opts, city_opts,
                climate_opts, default_opts, cooling_opts, climate_style)

    # callback to handle Clear All button
    @app.callback(
        [Output('company_name', 'value'),
         Output('time_period_category', 'value'),
         Output('measurement_category', 'value'),
         Output('metric_type', 'value'),
         Output('facility_scope', 'value'),
         Output('region', 'value'),
         Output('country', 'value'),
         Output('state', 'value'),
         Output('county', 'value'),
         Output('city', 'value'),
         Output('assigned_climate_zones', 'value'),
         Output('default_climate_zones', 'value'),
         Output('cooling_technologies', 'value')],
        [Input("clear-filters-btn", "n_clicks")],
        prevent_initial_call=True
    )

    def clear_all_filters(clear_clicks):
        if clear_clicks:
            # Clear all filter values
            return (None, [], [], [], [], None, None, None, None, None, None, None, None)
        return dash.no_update
    
    # Update chart
    @app.callback(
        [Output('pue-scatter-chart', 'figure'), Output('wue-scatter-chart', 'figure'), 
         #Output('summary', 'children')
         ],
        [Input("apply-filters-btn", "n_clicks"),
         Input("clear-filters-btn", "n_clicks")],
        [State('company_name', 'value'), State('time_period_category', 'value'), 
         State('measurement_category', 'value'), State('metric_type', 'value'), 
         State('facility_scope', 'value'), State('region', 'value'),
         State('country', 'value'), State('state', 'value'), State('county', 'value'),
         State('city', 'value'), State('assigned_climate_zones', 'value'), 
         State('default_climate_zones', 'value'), State('cooling_technologies', 'value')],
        prevent_initial_call=False
    )
    def update_dashboard_on_button_click(apply_clicks, clear_clicks, company, time_period_category, 
                                        measurement_category, metric_type, facility_scope,
                                        region, country, state, county, city, assigned_climate_zones, 
                                        default_climate_zones, cooling_technologies):
        
        # Get filtered data
        filtered_df = filter_data(df, company, time_period_category, measurement_category, metric_type, facility_scope,
                                region, country, state, county, city, assigned_climate_zones, default_climate_zones, cooling_technologies)
        
        ctx = dash.callback_context
        
        if ctx.triggered:
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if trigger_id == "clear-filters-btn":
                # Show all data in gray when cleared
                filtered_df = df.copy()
                filters_applied = False
                
            elif trigger_id == "apply-filters-btn":
                # Apply current filter states
                filtered_df = filter_data(df, company, time_period_category, measurement_category, 
                                         metric_type, facility_scope, region, country, state, 
                                         county, city, assigned_climate_zones, default_climate_zones, 
                                         cooling_technologies)
                filters_applied = any([
                    company, time_period_category, measurement_category, metric_type,
                    facility_scope, region, country, state, county, city,
                    assigned_climate_zones, default_climate_zones, cooling_technologies
                ])
            else:
                return dash.no_update, dash.no_update
        else:
            # Initial load
            filtered_df = df.copy()
            filters_applied = False

        # Split data by metric type in callback
        pue_filtered_df = filtered_df[filtered_df['metric'] == 'pue'].copy()
        pue_filtered_df = pue_filtered_df[pue_filtered_df['metric_value'].notna()]
        wue_filtered_df = filtered_df[filtered_df['metric'] == 'wue'].copy()
        wue_filtered_df = wue_filtered_df[wue_filtered_df['metric_value'].notna()]
        
        # Split unfiltered data for background
        pue_full_df = df[df['metric'] == 'pue'].copy()
        wue_full_df = df[df['metric'] == 'wue'].copy()

        pue_fig = create_pue_scatter_plot(filtered_df = pue_filtered_df, full_df=pue_full_df, filters_applied=filters_applied)
        wue_fig = create_wue_scatter_plot(filtered_df =  wue_filtered_df, full_df=wue_full_df, filters_applied=filters_applied)

        # # Create summary
        # active_filters = []
        # if filters_applied:
        #     if company: active_filters.append(f"Companies: {', '.join(company)}")
        #     if time_period_category: active_filters.append(f"Time Period: {', '.join(time_period_category)}")
        #     if measurement_category: active_filters.append(f"Measurement: {', '.join(measurement_category)}")
        #     if metric_type: active_filters.append(f"PUE/WUE Type: {', '.join(metric_type)}")
        #     if facility_scope: active_filters.append(f"Facility Scope: {', '.join(facility_scope)}")
        #     if region: active_filters.append(f"Region: {', '.join(region)}")
        #     if country: active_filters.append(f"Country: {', '.join(country)}")
        #     if state: active_filters.append(f"State: {', '.join(state)}")
        #     if county: active_filters.append(f"County: {', '.join(county)}")
        #     if city: active_filters.append(f"City: {', '.join(city)}")
        #     if assigned_climate_zones: active_filters.append(f"Climate Zone: {', '.join(assigned_climate_zones)}")
        #     if default_climate_zones: active_filters.append(f"Default Zone: {', '.join(default_climate_zones)}")
        #     if cooling_technologies: active_filters.append(f"Cooling Tech: {', '.join(cooling_technologies)}")
            
        # #status_text = f"Showing {len(filtered_df)} filtered records" if filters_applied else f"Showing all {len(filtered_df)} records"
        
        # summary = [
        #     html.H6("Active Filters:"),
        #     html.Ul([html.Li(f) for f in active_filters]) if active_filters else html.P("No filters applied"),
        #     #html.P(f"📊 {status_text}")
        # ]

        return pue_fig, wue_fig #summary
    
    # PUE vs WUE chart callback (company filter only)
    @app.callback(
        Output('pue-wue-scatter-chart', 'figure'),
        [Input("apply-filters-btn", "n_clicks"),
         Input("clear-filters-btn", "n_clicks")],
        [State('company_name', 'value')],
        prevent_initial_call=False
    )
    def update_pue_wue_scatter_plot(apply_clicks, clear_clicks, company):
        """Handle PUE vs WUE chart with company filter only"""
        
        ctx = dash.callback_context
        
        if ctx.triggered:
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if trigger_id == "clear-filters-btn":
                # Show all data when cleared
                pue_wue_filtered_df = df[df['metric'] == 'pue'].copy()
                pue_wue_filtered_df = pue_wue_filtered_df[pue_wue_filtered_df['wue_value'].notna()]
                filters_applied = False
                
            elif trigger_id == "apply-filters-btn":
                # Apply only company filter
                if company:
                    pue_wue_filtered_df = df[(df['metric'] == 'pue') & (df['company_name'].isin(company))].copy()
                    filters_applied = True
                else:
                    pue_wue_filtered_df = df[df['metric'] == 'pue'].copy()
                    filters_applied = False
                    
                pue_wue_filtered_df = pue_wue_filtered_df[pue_wue_filtered_df['wue_value'].notna()]
            else:
                return dash.no_update
        else:
            # Initial load - show all data
            pue_wue_filtered_df = df[df['metric'] == 'pue'].copy()
            pue_wue_filtered_df = pue_wue_filtered_df[pue_wue_filtered_df['wue_value'].notna()]
            filters_applied = False

        # Background data for PUE-WUE chart
        pue_wue_full_df = df[df['metric'] == 'pue'].copy()
        pue_wue_full_df = pue_wue_full_df[pue_wue_full_df['wue_value'].notna()]

        pue_wue_fig = create_pue_wue_scatter_plot(
            filtered_df=pue_wue_filtered_df, 
            full_df=pue_wue_full_df, 
            filters_applied=filters_applied
        )

        return pue_wue_fig
    
    # Modal callback
    @app.callback(
        [Output("graph-modal", "is_open"),
        Output("modal-title", "children"),
        Output("expanded-graph", "figure")],
        [Input("expand-pue", "n_clicks"),
        Input("expand-wue", "n_clicks"), 
        Input("expand-pue-wue", "n_clicks")],
        [State("graph-modal", "is_open"),
        State("pue-scatter-chart", "figure"),
        State("wue-scatter-chart", "figure"),
        State("pue-wue-scatter-chart", "figure")],
        prevent_initial_call=True 
    )
    def toggle_modal(pue_clicks, wue_clicks, comparison_clicks, is_open, 
                    pue_figure, wue_figure, pue_wue_figure):
        ctx = dash.callback_context
        
        if not ctx.triggered:
            return False, "", {}
            
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if button_id == "expand-pue":
            return not is_open, "Power Usage Effectiveness (PUE) - Expanded View", pue_figure or {}
        elif button_id == "expand-wue":  
            return not is_open, "Water Usage Effectiveness (WUE) - Expanded View", wue_figure or {}
        elif button_id == "expand-pue-wue":
            return not is_open, "PUE vs WUE Relationship - Expanded View", pue_wue_figure or {}
        
        return is_open, "", {}
    
    # Add these callbacks to your page or callbacks file
    @app.callback(
        Output("download-pue-scatter-chart", "data"),
        Input("download-btn-pue-scatter-chart", "n_clicks"),
        prevent_initial_call=True
    )
    def download_pue_data(n_clicks):
        # Get the project root directory (2 levels up from callbacks directory)
        root_dir = Path(__file__).parent.parent.parent
        input_path = root_dir / "data" / "DCEWM-PUEDataset.xlsx"

        # Debug print
        print(f"Looking for file at: {input_path}")
        print(f"File exists: {input_path.exists()}")

        return create_filtered_excel_download(
            input_path=input_path,
            output_filename="pue_data.xlsx",
            sheets_to_export=[
                "PUE",
                "Read Me",
            ],
            internal_prefix="_internal_",
            #skip_rows=1,
            n_clicks=n_clicks,
        )

    # @app.callback(
    #     Output("download-wue-scatter-chart", "data"),
    #     Input("download-btn-wue-scatter-chart", "n_clicks"),
    #     prevent_initial_call=True
    # )
    # def download_wue_data(n_clicks):
    #     return create_filtered_excel_download(
    #         input_path="data/wue_data.xlsx",
    #         output_filename="wue_data_export.xlsx",
    #         sheets_to_export=["WUE_Data"],
    #         n_clicks=n_clicks
    #     )

    @app.callback(
        Output("download-wue-scatter-chart", "data"),
        Input("download-btn-wue-scatter-chart", "n_clicks"),
        prevent_initial_call=True
    )
    def download_wue_data(n_clicks):
        # Get the project root directory (2 levels up from callbacks directory)
        root_dir = Path(__file__).parent.parent.parent
        input_path = root_dir / "data" / "DCEWM-WUEDataset.xlsx"

        # Debug print
        print(f"Looking for file at: {input_path}")
        print(f"File exists: {input_path.exists()}")

        return create_filtered_excel_download(
            input_path=input_path,
            output_filename="wue_data.xlsx",
            sheets_to_export=[
                "WUE",
                "Read Me",
            ],
            internal_prefix="_internal_",
            #skip_rows=1,
            n_clicks=n_clicks,
        )
    
    @app.callback(
        Output("download-pue-wue-scatter-chart", "data"),
        Input("download-btn-pue-wue-scatter-chart", "n_clicks"),
        prevent_initial_call=True
    )
    def download_pue_data(n_clicks):
        # Get the project root directory (2 levels up from callbacks directory)
        root_dir = Path(__file__).parent.parent.parent
        input_path = root_dir / "data" / "DCEWM-PUEDataset.xlsx"

        # Debug print
        print(f"Looking for file at: {input_path}")
        print(f"File exists: {input_path.exists()}")

        return create_filtered_excel_download(
            input_path=input_path,
            output_filename="pue_data.xlsx",
            sheets_to_export=[
                "PUE",
                "Read Me",
            ],
            internal_prefix="_internal_",
            #skip_rows=1,
            n_clicks=n_clicks,
        )
    
