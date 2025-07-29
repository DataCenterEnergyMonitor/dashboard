import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc

def create_pue_wue_filters(df):
    return html.Div([
        # Column 1: Company & Scope
        html.Div([
            html.H4("Company & Scope", className="filter-group-title"),
            html.Label("Company Name:", className="filter-label"),
            dcc.Dropdown(id='company', 
                         options=sorted(df['company'].unique()), 
                         multi=True, 
                         placeholder="Select companies",
                         className="filter-box"),
            html.Label("Time Period Category:", className="filter-label"),
            dcc.Checklist(
                id='time_period', 
                options=['Monthly', 'Quarterly', 'Biannual', 'Annual', 'Not evident'], 
                value=[],
                className="filter-box",
),
            html.Label("Measurement Category:", className="filter-label"),
            dcc.Checklist(
                id='measurement', 
                options=['Category 1', 'Category 2', 'Category 3', 'Not evident'], 
                value=[],
                className="filter-box",
),
            html.Label("PUE/WUE Type:", className="filter-label"),
            dcc.Checklist(
                id='pue_wue_type', 
                options=['Measured', 'Design'], 
                value=[],
                className="filter-box",
),
            html.Label("Facility Scope:", className="filter-label"),
            dcc.Checklist(
                id='facility_scope', 
                options=['Single location', 'Fleet-wide', 'Not evident'], 
                value=[],
                className="filter-box",
),
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
            dcc.Dropdown(id='climate_zone', options=[], multi=True, placeholder="Select climate zones", className="filter-box"),
            html.Label("Default Climate Zone:", className="filter-label"),
            dcc.Dropdown(id='default_zone', options=[], multi=True, placeholder="Select climate zones", className="filter-box"),
            html.Label("Cooling Technology:", className="filter-label"),
            dcc.Dropdown(id='cooling_tech', options=[], multi=True, placeholder="Select cooling technologies", className="filter-box"),
        ], style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}, id='climate-section'),
        
    ], style={'marginBottom': '30px'})


def create_pue_wue_filters_layout(df):
    return dbc.Accordion([
            dbc.AccordionItem([
            create_pue_wue_filters(df),
            html.Div(id='output-container'),
            ],
            title=html.Span([
                html.I(className="fas fa-filter me-2"), 
                "Filters"]),
                className="filter-accordion .accordion-item"),
        ],
        flush=True,
        start_collapsed=True,
        className="filter-accordion",)