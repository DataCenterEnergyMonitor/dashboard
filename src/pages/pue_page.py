from dash import html, dcc
import dash_bootstrap_components as dbc
from components.filter_manager import FilterManager, FilterConfig
from components.navbar import create_navbar
from components.filter_panel import create_filter_panel
from layouts.base_layout import create_base_layout
from components.download_button import create_download_button


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
            depends_on=None,
        ),
        FilterConfig(
            id="company",
            label="Company",
            column="company",
            multi=True,
            default_value="All",  # company_counts,  # List of top 5 companies
            show_all=True,
            depends_on=["facility_scope"],  # fleet/location
        ),
        FilterConfig(
            id="iea_region",
            label="Region",
            column="iea_region",
            multi=True,
            default_value="All",
            show_all=True,
            depends_on=["facility_scope", "company"],
        ),
        FilterConfig(
            id="iecc_climate_zone_s_",
            label="IECC Climate Zone",
            column="iecc_climate_zone_s_",
            multi=True,
            default_value=None,
            show_all=True,
            depends_on=["facility_scope", "company"],
        ),
        FilterConfig(
            id="pue_measurement_level",
            label="PUE Measurement Level",
            column="pue_measurement_level",
            multi=True,
            default_value="All",
            show_all=True,
            depends_on=None,
        ),
    ]

    # Create filter manager
    pue_filter_manager = FilterManager(app, "pue", pue_df, pue_filters)

    # Get filter components without download button
    filter_components = pue_filter_manager.create_filter_components()

    # Extract download button and component
    download_button = html.Button(
        "Download (.xlsx)",
        id=f"pue-download-button",
        style={
            "backgroundColor": "#4CAF50",
            "color": "white",
            "padding": "8px 16px",
            "border": "none",
            "borderRadius": "4px",
            "cursor": "pointer",
            "fontFamily": "Inter",
            "fontWeight": "500",
            "fontSize": "14px",
        },
    )
    download_component = dcc.Download(id=f"pue-download-data")

    content = html.Div(
        [
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
                                "Data Center Power Usage Effectiveness",
                                className="page-title",
                            ),
                            html.Div(
                                [
                                    html.P(
                                        [
                                            "Power Usage Effectiveness (PUE) is a ratio that measures data center energy efficiency.",
                                            html.Br(),
                                            "A PUE of 1.0 represents perfect efficiency.",
                                        ],
                                        style={
                                            "fontFamily": "Inter",
                                            "marginBottom": "10px",
                                            "color": "#404040",
                                            "fontSize": "16px",
                                        },
                                    )
                                ]
                            ),
                            # Download button above chart
                            html.Div(
                                [
                                    create_download_button(
                                        button_id="btn-download-pue-data",
                                        download_id="download-pue-data",
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
                            # Chart
                            html.Div(
                                [
                                    dcc.Graph(
                                        id="pue-scatter-chart",
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
            )
        ]
    )

    return create_base_layout(content)
