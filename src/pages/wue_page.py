from dash import html, dcc
from components.filter_manager import FilterManager, FilterConfig
from components.navbar import create_navbar

def create_wue_page(app, wue_df, company_counts):
    # Define WUE-specific filters with dependencies
    wue_filters = [
        FilterConfig(
            id="facility_scope",
            label="Facility Scope",
            column="facility_scope",
            multi=False,
            default_value=wue_df["facility_scope"].dropna().unique()[0],
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
        )
    ]
    
    # Initialize WUE-specific filter manager
    wue_filter_manager = FilterManager(app, "wue", wue_df, wue_filters)
    
    return html.Div([
        create_navbar(),
        html.Div([
            html.H1(
                "Data Center Water Usage Effectiveness (WUE): Trends by Company",
                style={'fontFamily': 'Roboto', 'fontWeight': '500', 'marginBottom': '30px', 'fontSize': '32px'}
            ),
            html.Div([
                html.P([
                    "Water Usage Effectiveness (WUE) measures the water efficiency of data centers.",
                    html.Br(),
                    "Lower WUE values indicate better water efficiency."
                ], style={
                    'fontFamily': 'Roboto',
                    'marginBottom': '20px',
                    'color': '#404040',
                    'maxWidth': '800px',
                    'fontSize': '16px'
                })
            ]),
            wue_filter_manager.create_filter_components(),
            dcc.Graph(id='wue-scatter-chart')
        ], style={'padding': '20px', 'maxWidth': '1200px', 'margin': 'auto'})
    ])

