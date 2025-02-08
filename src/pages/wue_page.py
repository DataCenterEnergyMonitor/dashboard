from dash import html, dcc
from components.filters import create_filters
from components.navbar import create_navbar

def create_wue_page(wue_df, wue_company_counts):
    return html.Div([
        create_navbar(),
        html.Div([
            html.H1(
                "Data Center Water Usage Effectiveness (WUE): Trends by Company",
                style={'fontFamily': 'Roboto', 'fontWeight': '500', 'marginBottom': '30px', 'fontSize': '32px'}
            ),
            
            html.Div([
                html.P(
                    "Water Usage Effectiveness (WUE) is a ratio that measures how efficiently a data center uses water.",
                    style={
                        'fontFamily': 'Roboto',
                        'marginBottom': '20px',
                        'color': '#404040',
                        'maxWidth': '800px',
                        'fontSize': '16px'
                    }
                )
        ]),
 
            create_filters(wue_df, wue_company_counts, chart_type='wue'),
            dcc.Graph(id='wue-scatter-chart')
        ], style={'padding': '20px', 'maxWidth': '1200px', 'margin': 'auto'})
    ])

