from dash import html, dcc
import dash_bootstrap_components as dbc
from components.filter_manager import FilterManager, FilterConfig
from components.navbar import create_navbar
from components.filter_panel import create_filter_panel

def create_pue_page(app, pue_df, company_counts):
    # Define PUE-specific filters with dependencies
    pue_filters = [
        FilterConfig(
            id="facility_scope",
            label="Facility Scope",
            column="facility_scope",
            multi=False,
            default_value="Fleet-wide",
            show_all=False,
            depends_on=None
        ),
        FilterConfig(
            id="company",
            label="Company",
            column="company",
            multi=True,
            default_value=company_counts,  # List of top 5 companies
            show_all=True,
            depends_on=["facility_scope"] #fleet/location
        ),
        
        FilterConfig(
            id="iea_region",
            label="Region",
            column="iea_region",
            multi=True,
            default_value="All",
            show_all=True,
            depends_on=['facility_scope', 'company']
        ),

        FilterConfig(
            id="iecc_climate_zone_s_",
            label="IECC Climate Zone",
            column="iecc_climate_zone_s_",
            multi=True,
            default_value=None,
            show_all=True,
            depends_on=['facility_scope', 'company']
        ),
        # FilterConfig(
        #     id="geographical_scope",
        #     label="Geographical Scope",
        #     column="geographical_scope",
        #     multi=True,
        #     default_value="All",
        #     show_all=True,
        #     depends_on=["facility_scope", "company"]
        # ),

        FilterConfig(
            id="pue_measurement_level",
            label="PUE Measurement Level",
            column="pue_measurement_level",
            multi=True,
            default_value="All",
            show_all=True,
            depends_on=None
        )
    ]
    
    # Initialize PUE-specific filter manager
    pue_filter_manager = FilterManager(app, "pue", pue_df, pue_filters)
    
    return html.Div([
        create_navbar(),
        # Main content container with flex layout
        html.Div([
            # Left side - Filter Panel
            create_filter_panel(
                pue_filter_manager.create_filter_components(),
                title="PUE Filters"
            ),
            
            # Right side - Main Content
            html.Div([
                html.H1(
                    "Data Center Power Usage Effectiveness (PUE)",
                    style={'fontFamily': 'Roboto', 'fontWeight': '500', 'marginBottom': '30px', 'fontSize': '32px'}
                ),
                html.Div([
                    html.P([
                        "Power Usage Effectiveness (PUE) is a ratio that measures data center energy efficiency.",
                        html.Br(),
                        "A PUE of 1.0 represents perfect efficiency."
                    ], style={
                        'fontFamily': 'Roboto',
                        'marginBottom': '20px',
                        'color': '#404040',
                        'maxWidth': '800px',
                        'fontSize': '16px'
                    })
                ]),
                dcc.Graph(id='pue-scatter-chart')
            ], style={
                'flex': '1',
                'padding': '20px',
                'maxWidth': '1200px'
            })
        ], style={
            'display': 'flex',
            'flexDirection': 'row',
            'minHeight': 'calc(100vh - 56px)',  # Subtract navbar height
            'backgroundColor': '#f8f9fa'
        })
    ])

