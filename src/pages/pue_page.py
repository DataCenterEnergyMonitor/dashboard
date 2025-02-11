from dash import html, dcc
from components.filter_manager import FilterManager, FilterConfig
from components.navbar import create_navbar

def create_pue_page(app, pue_df, company_counts):
    # Define PUE-specific filters with dependencies
    filters = [
        FilterConfig(
            id="facility_scope",
            label="Facility Scope",
            column="facility_scope",
            multi=False,
            default_value=pue_df["facility_scope"].dropna().unique()[0],
            show_all=False
        ),
        FilterConfig(
            id="company",
            label="Company",
            column="company",
            multi=True,
            default_value=company_counts,
            show_all=True,
            depends_on=["facility_scope"]  # Company depends on facility scope
        ),
        FilterConfig(
            id="geographical_scope",
            label="Geographical Scope",
            column="geographical_scope",
            multi=True,
            default_value="All",
            show_all=True,
            depends_on=["facility_scope", "company"]  # Geo scope depends on facility and company
        ),
        FilterConfig(
            id="pue_measurement_level",
            label="PUE Measurement Level",
            column="pue_measurement_level",
            multi=True,
            default_value="All",
            show_all=True,
            depends_on=["facility_scope", "company", "geographical_scope"]
        )
    ]
    
    # Initialize filter manager
    filter_manager = FilterManager(app, "pue", pue_df, filters)
    
    # Create layout
    return html.Div([
        create_navbar(),
        html.Div([
            html.H1(
                "Data Center Power Usage Effectiveness (PUE): Trends by Company",
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
            filter_manager.create_filter_components(),
            dcc.Graph(id='pue-scatter-chart')
        ], style={'padding': '20px', 'maxWidth': '1200px', 'margin': 'auto'})
    ])

