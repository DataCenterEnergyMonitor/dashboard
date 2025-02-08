from dash.dependencies import Output, Input
from dash import callback_context, no_update
from dash import dcc

class ChartCallbackManager:
    def __init__(self, app, data_dict, chart_configs):
        self.app = app
        self.data = data_dict
        self.configs = chart_configs
        self._register_all_callbacks()

    def _register_all_callbacks(self):
        """Register callbacks for all chart types"""
        for chart_type, config in self.configs.items():
            self.register_filter_callbacks(config)
            self.register_download_callbacks(config)

    def register_filter_callbacks(self, config):
        # Add callback for updating geographical scope options
        @self.app.callback(
            Output(config['geographical_scope_dropdown_id'], 'options'),
            [Input(config['company_dropdown_id'], 'value'),
             Input(config['scope_dropdown_id'], 'value')]
        )
        def update_geographical_scope_options(selected_companies, selected_scope):
            chart_data = self.data[config['chart_type']]
            df = chart_data['df']
            
            # Filter dataframe based on current selections
            filtered_df = df.copy()
            if selected_companies and "All" not in selected_companies:
                filtered_df = filtered_df[filtered_df["company"].isin(selected_companies)]
            if selected_scope:
                filtered_df = filtered_df[filtered_df["facility_scope"] == selected_scope]
            
            # Get available geographical scopes
            available_scopes = filtered_df["geographical_scope"].dropna().unique()
            options = [{"label": "All", "value": "All"}] + [
                {"label": scope, "value": scope} for scope in available_scopes
            ]
            return options

    def register_filter_callbacks(self, config):
        @self.app.callback(
            [Output(config['chart_id'], 'figure'),
             Output(config['company_dropdown_id'], 'value')],
            [Input(config['company_dropdown_id'], 'value'),
             Input(config['scope_dropdown_id'], 'value'),
             Input(config['geographical_scope_dropdown_id'], 'value')]
        )
        def update_chart(selected_companies, selected_scope, selected_geographical_scope):
            chart_type = config['chart_type']
            chart_data = self.data[chart_type]
            filtered_df = self._filter_dataframe(
                chart_data['df'],
                selected_companies,
                selected_scope,
                selected_geographical_scope
            )
            
            figure = config['chart_creator'](
                filtered_df=filtered_df,
                selected_scope=selected_scope,
                industry_avg=chart_data['industry_avg']
            )
            return figure, selected_companies

    def register_download_callbacks(self, config):
        """Register callbacks for data downloads"""
        @self.app.callback(
            Output(config['download_data_id'], "data"),
            [Input(config['download_button_id'], "n_clicks"),
             Input(config['company_dropdown_id'], 'value'),
             Input(config['scope_dropdown_id'], 'value'),
             Input(config['geographical_scope_dropdown_id'], 'value')]
        )
        def download_data(n_clicks, selected_companies, selected_scope, selected_geographical_scope):
            if not n_clicks or callback_context.triggered_id != config['download_button_id']:
                return no_update
                
            chart_data = self.data[config['chart_type']]
            filtered_df = self._filter_dataframe(
                chart_data['df'],
                selected_companies,
                selected_scope,
                selected_geographical_scope
            )
            return dcc.send_data_frame(filtered_df.to_csv, config['filename'])

    def _filter_dataframe(self, df, selected_companies, selected_scope, selected_geographical_scope):
        """Filter DataFrame based on selected companies, facility scope, and geographic scope"""
        filtered_df = df.dropna(subset=["facility_scope"])
        
        if selected_companies:
            if "All" in selected_companies:
                if len(selected_companies) > 1:
                    selected_companies.remove("All")
                    filtered_df = filtered_df[filtered_df["company"].isin(selected_companies)]
            else:
                filtered_df = filtered_df[filtered_df["company"].isin(selected_companies)]
        
        if selected_scope:
            filtered_df = filtered_df[filtered_df["facility_scope"] == selected_scope]
        
        if selected_geographical_scope and selected_geographical_scope != "All":
            if isinstance(selected_geographical_scope, list):
                filtered_df = filtered_df[filtered_df["geographical_scope"].isin(selected_geographical_scope)]
            else:
                filtered_df = filtered_df[filtered_df["geographical_scope"] == selected_geographical_scope]
        
        return filtered_df
