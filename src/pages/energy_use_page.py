from dash import html, dcc
from datetime import datetime
import dash_bootstrap_components as dbc
from components.filter_manager import FilterManager, FilterConfig
from components.filter_panel import create_filter_panel
from components.download_button import create_download_button
from layouts.base_layout import create_base_layout


def get_energy_use_filters():
    current_reporting_year = datetime.now().year - 1
    previous_reporting_year = current_reporting_year - 1

    return [
        FilterConfig(
            id="reported_data_year",
            label="Reporting Year",
            column="reported_data_year",
            type="dropdown",
            multi=False,
            default_value=previous_reporting_year,
            show_all=False,
            depends_on=None,
        ),
        FilterConfig(
            id="reporting_scope",
            label="Reporting Scope",
            column="reporting_scope",
            type="radio",
            multi=False,
            default_value="All",
            show_all=True,
            depends_on=None,
            options={
                "options": [
                    {"label": "Company Wide", "value": "Company Wide Electricity Use"},
                    {"label": "Data Centers", "value": "Data Center Electricity Use"},
                    {"label": "All", "value": "All"},
                ]
            },
        ),
        FilterConfig(
            id="company_name",
            label="Company",
            column="company_name",
            type="dropdown",
            multi=True,
            default_value="All",
            show_all=True,
            depends_on=None,
        ),
    ]


def create_energy_use_page(app, energy_use_df):
    # Define energy use filters
    energy_filters = get_energy_use_filters()

    # Initialize filter manager
    filter_manager = FilterManager(app, "energy-use", energy_use_df, energy_filters)
    filter_components = filter_manager.create_filter_components()

    content = html.Div(
        [
            # Add download component at the top level
            dcc.Download(id="download-energy-use-data"),
            # Main content container
            html.Div(
                [
                    # Left side - Filter Panel
                    html.Div(
                        [create_filter_panel(filter_components)],
                        style={"width": "260px", "flexShrink": "0"},
                    ),
                    # Right side - Main Content
                    html.Div(
                        [
                            html.H1(
                                "Data Center Energy Usage by Company",
                                className="page-title",
                            ),
                            html.Div(
                                [
                                    html.P(
                                        [
                                            "Compare electricity usage across different companies and reporting scopes.",
                                            html.Br(),
                                            "Use the filters to select specific years, companies, and reporting scopes.",
                                        ],
                                        className="body-text",
                                    )
                                ]
                            ),
                            # Download button
                            html.Div(
                                [
                                    create_download_button(
                                        button_id="btn-download-energy-use-data",
                                        download_id="download-energy-use-data",
                                    ),
                                ],
                                style={
                                    "display": "flex",
                                    "justifyContent": "right",
                                    "marginBottom": "10px",
                                    "width": "90%",
                                    "margin": "0 auto",
                                    "paddingRight": "10px",
                                    "paddingBottom": "10px",
                                },
                            ),
                            # Bar Chart
                            html.Div(
                                [
                                    dcc.Graph(
                                        id="energy-use-bar-chart",
                                        style={
                                            "height": "calc(100vh - 400px)",
                                            "width": "100%",
                                        },
                                        config={"responsive": True},
                                    )
                                ],
                                style={"width": "90%", "margin": "0 auto"},
                            ),
                        ],
                        style={
                            "flex": "1",
                            "padding": "30px",
                            "minWidth": "0",
                            "overflow": "hidden",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "flexDirection": "row",
                    "minHeight": "calc(100vh - 40px)",
                    "backgroundColor": "#f8f9fa",
                },
            ),
        ]
    )

    return create_base_layout(content)
