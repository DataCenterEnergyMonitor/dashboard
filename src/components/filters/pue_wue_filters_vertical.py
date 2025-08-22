import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc

def create_pue_wue_filters(df):
    return html.Div([
        # Sidebar container
        html.Div([
            # Header
            html.Div([
                html.Span([
                    html.I(className="fas fa-filter me-2"),
                    ""
                ]),
            ]),
            
            # Scrollable filter content
            html.Div([
                # Company & Scope Section
                html.Div([
                    html.H5("Company & Scope", 
                           className="filter-section-title",
                           style={
                               "color": "#34495e",
                               "fontSize": "1.1rem",
                               "fontWeight": "600",
                               "marginBottom": "15px",
                               "marginTop": "20px"
                           }),
                    
                    html.Label("Company/Organization Name:", className="filter-label"),
                    dcc.Dropdown(
                        id='company_name', 
                        options=sorted(df['company_name'].unique()), 
                        multi=True, 
                        persistence=True,
                        persistence_type="session",
                        placeholder="Select companies",
                        className="filter-box mb-3"
                    ),
                    
                    html.Label("Time Period Category:", className="filter-label"),
                    dcc.Checklist(
                        id='time_period_category', 
                        options=[{'label': str(val), 'value': val} for val in sorted(df['time_period_category'].dropna().unique())],
                        value=[],
                        persistence=True,
                        persistence_type="session",
                        className="filter-box mb-3"
                    ),
                    
                    html.Label("Measurement Category:", className="filter-label"),
                    dcc.Checklist(
                        id='measurement_category', 
                        options=[{'label': str(val), 'value': val} for val in sorted(df['measurement_category'].dropna().unique())], 
                        value=[],
                        persistence=True,
                        persistence_type="session",
                        className="filter-box mb-3"
                    ),
                    
                    html.Label("PUE/WUE Type:", className="filter-label"),
                    dcc.Checklist(
                        id='metric_type', 
                        options=[{'label': str(val), 'value': val} for val in sorted(df['metric_type'].dropna().unique())], 
                        value=[],
                        persistence=True,
                        persistence_type="session",
                        className="filter-box mb-3"
                    ),
                    
                    html.Label("Facility Scope:", className="filter-label"),
                    dcc.Checklist(
                        id='facility_scope', 
                        options=[{'label': str(val), 'value': val} for val in sorted(df['facility_scope'].dropna().unique())],  
                        value=[],
                        persistence=True,
                        persistence_type="session",
                        className="filter-box mb-4"
                    ),
                ]),
                
                # Facility Location Section
                html.Div([
                    html.H5("Facility Location", 
                           className="filter-section-title",
                           style={
                               "color": "#34495e",
                               "fontSize": "1.1rem",
                               "fontWeight": "600",
                               "marginBottom": "15px",
                               "marginTop": "20px"
                           }),
                    
                    html.Label("Region:", className="filter-label"),
                    dcc.Dropdown(
                        id='region', 
                        options=[], 
                        multi=True, 
                        placeholder="Select regions",
                        persistence=True,
                        persistence_type="session",
                        className="filter-box mb-2"
                    ),
                    
                    html.Label("Country:", className="filter-label"),
                    dcc.Dropdown(
                        id='country', 
                        options=[], 
                        multi=True, 
                        placeholder="Select countries",
                        persistence=True,
                        persistence_type="session",
                        className="filter-box mb-2"
                    ),
                    
                    html.Label("State/Province:", className="filter-label"),
                    dcc.Dropdown(
                        id='state', 
                        options=[], 
                        multi=True, 
                        placeholder="Select states",
                        persistence=True,
                        persistence_type="session",
                        className="filter-box mb-2"
                    ),
                    
                    html.Label("County:", className="filter-label"),
                    dcc.Dropdown(
                        id='county', 
                        options=[], 
                        multi=True, 
                        placeholder="Select counties", 
                        persistence=True,
                        persistence_type="session",
                        className="filter-box mb-2"
                    ),
                    
                    html.Label("City:", className="filter-label"),
                    dcc.Dropdown(
                        id='city', 
                        options=[], 
                        multi=True, 
                        placeholder="Select cities", 
                        persistence=True,
                        persistence_type="session",
                        className="filter-box mb-2"
                    ),
                ]),
                
                # Climate & Cooling Section
                html.Div([
                    html.H5("Climate & Cooling", 
                           className="filter-section-title",
                           style={
                               "color": "#34495e",
                               "fontSize": "1.1rem",
                               "fontWeight": "600",
                               "marginBottom": "15px",
                               "marginTop": "20px"
                           }),
                    
                    html.Label(["Assigned Climate Zone:", 
                               dbc.Tooltip(
                                        "Climate zones impact data center energy use. " \
                                        "Cooler climates enable efficient cooling methods that require less energy, " \
                                        "while hotter climates need energy-intensive cooling systems, potentially leading to higher PUEs.",
                                        target="assigned-climate-zone-tooltip",
                                        placement="right"
                                    ),
                                html.I(
                                className="fas fa-info-circle ms-1",
                                id="assigned-climate-zone-tooltip",
                                style={"fontSize": "12px", "cursor": "help", "color": "#007bff"},
                            )
                       ],   className="filter-label"),
                    dcc.Dropdown(
                        id='assigned_climate_zones', 
                        options=[], 
                        multi=True, 
                        placeholder="Select climate zones", 
                        persistence=True,
                        persistence_type="session",
                        className="filter-box mb-2"
                    ),
                    
                    html.Label("Default Climate Zone:", className="filter-label"),
                    dcc.Dropdown(
                        id='default_climate_zones', 
                        options=[], 
                        multi=True, 
                        placeholder="Select climate zones", 
                        persistence=True,
                        persistence_type="session",
                        className="filter-box mb-2"
                    ),
                    
                    html.Label("Cooling Technology:", className="filter-label"),
                    dcc.Dropdown(
                        id='cooling_technologies', 
                        options=[], 
                        multi=True, 
                        placeholder="Select cooling technologies", 
                        persistence=True,
                        persistence_type="session",
                        className="filter-box mb-2"
                    ),
                ],id='climate-section'),
            ], style={
                "overflowY": "auto",
                "maxHeight": "calc(100vh - 200px)",  # Allow scrolling
                "paddingRight": "10px",
                "paddingBottom": "50px" 
            }),
            
            # Fixed buttons at bottom
            html.Div([
                dbc.ButtonGroup([
                    dbc.Button(
                        "Apply Filters",
                        id="apply-filters-btn",
                        color="primary",
                        size="sm",
                        n_clicks=0,
                        className="mb-2",
                        style={"width": "100%", "borderRadius": "5px"}
                    ),
                    dbc.Button(
                        "Clear All",
                        id="clear-filters-btn",
                        color="outline-secondary",
                        size="sm",
                        n_clicks=0,
                        style={"width": "100%", "borderRadius": "5px"}
                    )
                ], vertical=True, className="w-100")
            ], style={
                "position": "sticky",
                "bottom": "0",
                "backgroundColor": "#f8f9fa",
                "padding": "15px 0",
                "marginTop": "20px",
                "borderTop": "1px solid #dee2e6"
            }),
            
            # Hidden div to store applied filter state
            html.Div(id="applied-filters-store", style={"display": "none"}),
            
        ], style={
            "width": "300px",
            "height": "calc(100vh - 100px)",  # ✅ Subtract navbar height
            "position": "fixed",
            "left": "0",
            "top": "100px", 
            #"backgroundColor": "#f8f9fa",
            "borderRight": "1px solid #dee2e6",
            "padding": "20px",
            "zIndex": "999",  # Lower than navbar but higher than content
            #"boxShadow": "2px 0 5px rgba(0,0,0,0.1)",
            #"overflowY": "auto"
        })
    ])

### Alternative implementation with accordion for better organization
# def create_pue_wue_filters(df):
#     return html.Div([
#         # Sidebar container
#         html.Div([
#             # Header
#             html.Div([
#                 html.Span([
#                     html.I(className="fas fa-filter me-2"),
#                     html.H5("Filters", style={"display": "inline", "marginLeft": "5px"})
#                 ]),
#             ], style={"marginBottom": "20px"}),
            
#             # Scrollable filter content with accordion
#             html.Div([
#                 dbc.Accordion([
#                     # Company & Scope Section
#                     dbc.AccordionItem([
#                         html.Label("Company Name:", className="filter-label"),
#                         dcc.Dropdown(
#                             id='company_name', 
#                             options=sorted(df['company_name'].unique()), 
#                             multi=True, 
#                             persistence=True,
#                             persistence_type="session",
#                             placeholder="Select companies",
#                             className="filter-box mb-3"
#                         ),
                        
#                         html.Label("Time Period Category:", className="filter-label"),
#                         dcc.Checklist(
#                             id='time_period_category', 
#                             options=[{'label': str(val), 'value': val} for val in sorted(df['time_period_category'].dropna().unique())],
#                             value=[],
#                             persistence=True,
#                             persistence_type="session",
#                             className="filter-box mb-3"
#                         ),
                        
#                         html.Label("Measurement Category:", className="filter-label"),
#                         dcc.Checklist(
#                             id='measurement_category', 
#                             options=[{'label': str(val), 'value': val} for val in sorted(df['measurement_category'].dropna().unique())], 
#                             value=[],
#                             persistence=True,
#                             persistence_type="session",
#                             className="filter-box mb-3"
#                         ),
                        
#                         html.Label("PUE/WUE Type:", className="filter-label"),
#                         dcc.Checklist(
#                             id='metric_type', 
#                             options=[{'label': str(val), 'value': val} for val in sorted(df['metric_type'].dropna().unique())], 
#                             value=[],
#                             persistence=True,
#                             persistence_type="session",
#                             className="filter-box mb-3"
#                         ),
                        
#                         html.Label("Facility Scope:", className="filter-label"),
#                         dcc.Checklist(
#                             id='facility_scope', 
#                             options=[{'label': str(val), 'value': val} for val in sorted(df['facility_scope'].dropna().unique())],  
#                             value=[],
#                             persistence=True,
#                             persistence_type="session",
#                             className="filter-box mb-3"
#                         ),
#                     ], title="Company & Scope", 
#                     item_id="company-scope",
#                            style={
#                                 "border": "none",
#                                 "background": "transparent",
#                                 "boxShadow": "none"
#                             }),
                    
#                     # Facility Location Section
#                     dbc.AccordionItem([
#                         html.Label("Region:", className="filter-label"),
#                         dcc.Dropdown(
#                             id='region', 
#                             options=[], 
#                             multi=True, 
#                             placeholder="Select regions",
#                             persistence=True,
#                             persistence_type="session",
#                             className="filter-box mb-2"
#                         ),
                        
#                         html.Label("Country:", className="filter-label"),
#                         dcc.Dropdown(
#                             id='country', 
#                             options=[], 
#                             multi=True, 
#                             placeholder="Select countries",
#                             persistence=True,
#                             persistence_type="session",
#                             className="filter-box mb-2"
#                         ),
                        
#                         html.Label("State/Province:", className="filter-label"),
#                         dcc.Dropdown(
#                             id='state', 
#                             options=[], 
#                             multi=True, 
#                             placeholder="Select states",
#                             persistence=True,
#                             persistence_type="session",
#                             className="filter-box mb-2"
#                         ),
                        
#                         html.Label("County:", className="filter-label"),
#                         dcc.Dropdown(
#                             id='county', 
#                             options=[], 
#                             multi=True, 
#                             placeholder="Select counties", 
#                             persistence=True,
#                             persistence_type="session",
#                             className="filter-box mb-2"
#                         ),
                        
#                         html.Label("City:", className="filter-label"),
#                         dcc.Dropdown(
#                             id='city', 
#                             options=[], 
#                             multi=True, 
#                             placeholder="Select cities", 
#                             persistence=True,
#                             persistence_type="session",
#                             className="filter-box mb-2"
#                         ),
#                     ], title="Facility Location", item_id="location"),
                    
#                     # Climate & Cooling Section
#                     dbc.AccordionItem([
#                         html.Label("Assigned Climate Zone:", className="filter-label"),
#                         dcc.Dropdown(
#                             id='assigned_climate_zones', 
#                             options=[], 
#                             multi=True, 
#                             placeholder="Select climate zones", 
#                             persistence=True,
#                             persistence_type="session",
#                             className="filter-box mb-2"
#                         ),
                        
#                         html.Label("Default Climate Zone:", className="filter-label"),
#                         dcc.Dropdown(
#                             id='default_climate_zones', 
#                             options=[], 
#                             multi=True, 
#                             placeholder="Select climate zones", 
#                             persistence=True,
#                             persistence_type="session",
#                             className="filter-box mb-2"
#                         ),
                        
#                         html.Label("Cooling Technology:", className="filter-label"),
#                         dcc.Dropdown(
#                             id='cooling_technologies', 
#                             options=[], 
#                             multi=True, 
#                             placeholder="Select cooling technologies", 
#                             persistence=True,
#                             persistence_type="session",
#                             className="filter-box mb-2"
#                         ),
#                     ], title="Climate & Cooling", item_id="climate-section", id='climate-section'),
                    
#                 ], start_collapsed=False, 
#                 always_open=True,  # Multiple sections can be open
#                 flush=True,
#                    style={
#                         "border": "none",
#                         "background": "transparent"
#                     })  
                
#             ], style={
#                 "overflowY": "auto",
#                 "maxHeight": "calc(100vh - 300px)",
#                 "paddingRight": "10px",
#                 "paddingBottom": "20px"
#             }),
            
#             # Fixed buttons at bottom
#             html.Div([
#                 dbc.ButtonGroup([
#                     dbc.Button(
#                         "Apply Filters",
#                         id="apply-filters-btn",
#                         color="primary",
#                         size="sm",
#                         n_clicks=0,
#                         className="mb-2",
#                         style={"width": "100%", "borderRadius": "5px"}
#                     ),
#                     dbc.Button(
#                         "Clear All",
#                         id="clear-filters-btn",
#                         color="outline-secondary",
#                         size="sm",
#                         n_clicks=0,
#                         style={"width": "100%", "borderRadius": "5px"}
#                     )
#                 ], vertical=True, className="w-100")
#             ], style={
#                 "backgroundColor": "#f8f9fa",
#                 "padding": "15px 0",
#                 "borderTop": "1px solid #dee2e6"
#             }),
            
#             html.Div(id="applied-filters-store", style={"display": "none"}),
            
#         ], style={
#             "width": "300px",
#             "height": "calc(100vh - 100px)",
#             "position": "fixed",
#             "left": "0",
#             "top": "100px", 
#             "backgroundColor": "#f8f9fa",
#             "borderRight": "1px solid #dee2e6",
#             "padding": "20px",
#             "zIndex": "999",
#             "display": "flex",
#             "flexDirection": "column"
#         })
#     ])

def get_options(column, filtered_df):
    """Get unique options from filtered dataframe"""
    return [{'label': val, 'value': val} for val in sorted(filtered_df[column].unique())]