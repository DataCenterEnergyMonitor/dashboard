from dash import html, dcc
from components.filters import create_filters
from components.navbar import create_navbar

filter_config = {
    'facility_scope': True,
    'company': True,
    'geographical_scope': True  # This filter won't be shown
}

def create_pue_page(pue_df, company_counts):
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
            create_filters(pue_df, company_counts, chart_type='pue', filter_config=filter_config),
            dcc.Graph(id='pue-scatter-chart')
        ], style={'padding': '20px', 'maxWidth': '1200px', 'margin': 'auto'})
    ])

