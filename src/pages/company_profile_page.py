from dash import html, dcc, dash_table
from datetime import datetime
import dash_bootstrap_components as dbc
from components.filter_manager import FilterManager, FilterConfig
from components.filter_panel import create_filter_panel
from components.download_button import create_download_button
from layouts.base_layout import create_base_layout
from components.collapsible_table import create_category_section

current_reporting_year = datetime.now().year - 1
previous_reporting_year = current_reporting_year - 1


def get_company_profile_filters():
    return [
        FilterConfig(
            id="company_name",
            label="Company",
            column="company_name",
            type="dropdown",
            multi=False,
            default_value=None,
            show_all=False,
            depends_on=None,
        ),
    ]


def create_company_profile_page(app, company_profile_df, energy_use_df):
    companies = sorted(energy_use_df["company_name"].unique())
    default_company = companies[0] if companies else None

    content = html.Div(
        [
            dcc.Download(id="download-company-profile-data"),
            # Main content container with consistent padding
            html.Div(
                [
                    # Page Title
                    html.H1(
                        "Company Reporting Profile",
                        className="page-title",
                    ),
                    # Dropdown Filter Container
                    html.Div(
                        dcc.Dropdown(
                            id="company-profile-dropdown",
                            options=[{"label": c, "value": c} for c in companies],
                            placeholder="Select a company",
                            value=default_company,
                            style={
                                "width": "100%",
                                "fontFamily": "Inter",
                                "fontSize": "16px",
                            },
                        ),
                        style={
                            "maxWidth": "400px",
                            "minWidth": "340px",
                            "marginBottom": "24px",
                        },
                    ),
                    # Flex container for main content
                    html.Div(
                        [
                            # Left side content container
                            html.Div(
                                [
                                    # Company Profile Content
                                    html.H2(
                                        id="company-data-title",
                                        children=f"{default_company} Reporting Profile"
                                        if default_company
                                        else "Select a Company",
                                        style={
                                            "fontFamily": "Inter",
                                            "fontWeight": "500",
                                            "fontSize": "24px",
                                            "marginBottom": "16px",
                                            "color": "#2c3e50",
                                        },
                                    ),
                                    html.Div(id="collapsible-tables-container"),
                                ],
                                style={
                                    "flex": "0 0 auto",
                                    "backgroundColor": "white",
                                    "padding": "16px",
                                    "borderRadius": "4px",
                                    "boxShadow": "0 1px 3px rgba(0,0,0,0.12)",
                                    "minWidth": "340px",
                                    "maxWidth": "400px",
                                    "width": "100%",
                                },
                            ),
                            # Right side chart
                            html.Div(
                                [
                                    html.H2(
                                        "Energy Consumption Over Time",
                                        className="section-title",
                                        style={
                                            "fontFamily": "Inter",
                                            "fontWeight": "500",
                                            "fontSize": "24px",
                                            "marginBottom": "16px",
                                            "color": "#2c3e50",
                                        },
                                    ),
                                    dcc.Graph(
                                        id="company-profile-bar-chart",
                                        style={"height": "500px"},
                                        config={"responsive": True},
                                    ),
                                ],
                                style={
                                    "flex": "1",
                                    "backgroundColor": "white",
                                    "padding": "16px",
                                    "borderRadius": "4px",
                                    "boxShadow": "0 1px 3px rgba(0,0,0,0.12)",
                                    "marginLeft": "16px",
                                    "minWidth": "0",  # Allow shrinking below flex-basis
                                },
                            ),
                        ],
                        style={
                            "display": "flex",
                            "gap": "16px",
                            "width": "100%",
                            "flexWrap": "wrap",  # Allow wrapping on smaller screens
                        },
                    ),
                ],
                style={
                    "maxWidth": "1600px",
                    "margin": "0 auto",
                    "padding": "10px",
                    "width": "100%",
                },
            ),
        ]
    )

    return create_base_layout(content)
