import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc

def create_pue_wue_filters(df):
    return html.Div([
        # Column 1: Company & Scope
        html.Div([
            html.H4("Company & Scope", className="filter-group-title"),
            html.Label("Company Name:", className="filter-label"),
            dcc.Dropdown(id='company_name', 
                         options=sorted(df['company_name'].unique()), 
                         multi=True, 
                         placeholder="Select companies",
                         className="filter-box"),
            html.Label("Time Period Category:", className="filter-label"),
            dcc.Checklist(
                id='time_period_category', 
                options=['Monthly', 'Quarterly', 'Biannual', 'Annual', 'Not evident'], 
                value=[],
                className="filter-box"),
            html.Label("Measurement Category:", className="filter-label"),
            dcc.Checklist(
                id='measurement_category', 
                options=['Category 1', 'Category 2', 'Category 3', 'Not evident'], 
                value=[],
                className="filter-box"),
            html.Label("PUE/WUE Type:", className="filter-label"),
            dcc.Checklist(
                id='metric_type', 
                options=['Measured', 'Design'], 
                value=[],
                className="filter-box"),
            html.Label("Facility Scope:", className="filter-label"),
            dcc.Checklist(
                id='facility_scope', 
                options=['Single location', 'Fleet-wide', 'Not evident'], 
                value=[],
                className="filter-box"),
        ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
        
        # Column 2: Facility Location
        html.Div([
            html.H4("Facility Location", className="filter-group-title"),
            html.Label("Region:", className="filter-label"),
            dcc.Dropdown(id='region', 
                         options=[], 
                         multi=True, 
                         placeholder="Select regions",
                         className="filter-box"),
            html.Label("Country:", className="filter-label"),
            dcc.Dropdown(id='country', 
                         options=[], 
                         multi=True, 
                         placeholder="Select countries",
                         className="filter-box"),
            html.Label("State/Province:", className="filter-label"),
            dcc.Dropdown(id='state', 
                         options=[], 
                         multi=True, 
                         placeholder="Select states",
                         className="filter-box"),
            html.Label("County:", className="filter-label"),
            dcc.Dropdown(id='county', options=[], multi=True, placeholder="Select counties", className="filter-box"),
            html.Label("City:", className="filter-label"),
            dcc.Dropdown(id='city', options=[], multi=True, placeholder="Select cities", className="filter-box"),
        ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
        
        # Column 3: Climate & Cooling
        html.Div([
            html.H4("Climate & Cooling", className="filter-group-title"),
            html.Label("Assigned Climate Zone:", className="filter-label"),
            dcc.Dropdown(id='assigned_climate_zones', options=[], multi=True, placeholder="Select climate zones", className="filter-box"),
            html.Label("Default Climate Zone:", className="filter-label"),
            dcc.Dropdown(id='default_climate_zones', options=[], multi=True, placeholder="Select climate zones", className="filter-box"),
            html.Label("Cooling Technology:", className="filter-label"),
            dcc.Dropdown(id='cooling_technologies', options=[], multi=True, placeholder="Select cooling technologies", className="filter-box"),
        ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}, id='climate-section'),
        
        # Apply/Clear buttons
        dbc.Row([
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button(
                        ["Apply"],
                        id="apply-filters-btn",
                        color="primary",
                        size="sm",
                        n_clicks=0,
                        style={"marginRight": "10px", "borderRadius": "20px"}

                    ),
                    dbc.Button(
                        ["Clear All"],
                        id="clear-filters-btn",
                        color="outline-secondary",
                        size="sm",
                        n_clicks=0,
                        style={"marginRight": "10px", "borderRadius": "20px"}
                    )
                ], className="w-100")
            ], width=4, className="text-center")
        ], className="mt-3 mb-3"),
        
        # Hidden div to store applied filter state
        html.Div(id="applied-filters-store", style={"display": "none"}),
    ], style={'marginBottom': '30px'})

def get_options(column, filtered_df):
    """Get unique options from filtered dataframe"""
    return [{'label': val, 'value': val} for val in sorted(filtered_df[column].unique())]