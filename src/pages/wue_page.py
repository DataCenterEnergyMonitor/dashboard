from dash import html, dcc
import dash_bootstrap_components as dbc
from components.filter_manager import FilterManager, FilterConfig
from components.filter_panel import create_filter_panel
from components.download_button import create_download_button
from layouts.base_layout import create_base_layout

def create_wue_page(app, wue_df, company_counts):
    # Define WUE-specific filters with dependencies
    wue_filters = [
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
            default_value="All",
            show_all=True,
            depends_on=["facility_scope"]
        )
    ]
    
    # Initialize WUE-specific filter manager
    wue_filter_manager = FilterManager(app, "wue", wue_df, wue_filters)

    # Get filter components without download button
    filter_components = wue_filter_manager.create_filter_components()
    
    content = html.Div([
        # Main content container
        html.Div([
            # Left side - Filter Panel
            html.Div([
                create_filter_panel(filter_components)
            ], style={
                'width': '260px',
                'flexShrink': '0'
            }),

            # Right side - Main Content
            html.Div([
                html.H1(
                    "Data Center Water Usage Effectiveness: Trends by Company",
                    className="page-title"
                ),
                html.Div([
                    html.P([
                        "Water Usage Effectiveness (WUE) measures the water efficiency of data centers.",
                        html.Br(),
                        "Lower WUE values indicate better water efficiency."
                    ], className="body-text")
                ]),
            # Download button above charts
            html.Div([

                create_download_button(
                    button_id="btn-download-wue-data",
                        download_id="download-wue-data"
                    ),
                ], style={
                    'display': 'flex',
                    'justifyContent': 'right',
                    'marginBottom': '10px',
                    'width': '90%',
                    'margin': '0 auto',
                    'paddingRight': '10px',
                    'paddingBottom': '10px'
                }),
                # Chart
                html.Div([
                    dcc.Graph(
                        id='wue-scatter-chart',
                        style={
                            'height': 'calc(100vh - 400px)',
                            'width': '100%'
                        },
                        config={
                            'responsive': True
                        }
                    )
                ], style={
                    'width': '90%',
                    'margin': '0 auto'
                })
            ], style={
                'flex': '1',
                'padding': '30px',
                'minWidth': '0',
                'overflow': 'hidden'
            })
        ], style={
            'display': 'flex',
            'flexDirection': 'row',
            'minHeight': 'calc(100vh - 40px)',
            'backgroundColor': '#f8f9fa'
        })
    ])

    return create_base_layout(content)

