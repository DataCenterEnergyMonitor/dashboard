from dash import html, dcc, dash_table
from datetime import datetime
import dash_bootstrap_components as dbc
from components.filter_manager import FilterManager, FilterConfig
from components.filter_panel import create_filter_panel
from components.download_button import create_download_button
from layouts.base_layout import create_base_layout

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

    # Prepare the table columns with renamed headers
    table_columns = [
        {"name": "Reporting Metric", "id": "metric", "presentation": "markdown"},
        {"name": "Status", "id": "status", "presentation": "markdown"},
    ]

    content = html.Div(
        [
            dcc.Download(id="download-company-profile-data"),
            html.Div(
                [
                    # Page Title
                    html.H1(
                        "Company Reporting Profile",
                        className="page-title",
                        style={"marginBottom": "24px"},
                    ),
                    # Simple Dropdown Filter with default value
                    html.Div(
                        [
                            dcc.Dropdown(
                                id="company-profile-dropdown",
                                options=[{"label": c, "value": c} for c in companies],
                                placeholder="Select a company",
                                value=default_company,  # Set default value
                                style={"width": "300px"},
                            ),
                        ],
                        style={
                            "marginBottom": "24px",
                        },
                    ),
                    # Chart and Table Container
                    html.Div(
                        [
                            # Left side - Table (25% width)
                            html.Div(
                                [
                                    html.H2(
                                        id="company-data-title",
                                        children=f"{default_company} Profile"
                                        if default_company
                                        else "Select a Company",
                                        style={
                                            "fontFamily": "Inter",
                                            "fontWeight": "500",
                                            "fontSize": "18px",
                                            "marginBottom": "10px",
                                            "color": "#2c3e50",
                                        },
                                    ),
                                    dash_table.DataTable(
                                        id="company-profile-data-table",
                                        columns=[
                                            {
                                                "name": "REPORTING METRIC",
                                                "id": "metric",
                                            },
                                            {"name": "STATUS", "id": "status"},
                                        ],
                                        data=[],
                                        style_table={
                                            "overflowY": "hidden",
                                            "overflowX": "hidden",
                                            "height": "auto",
                                            "width": "100%",
                                        },
                                        style_cell={
                                            "textAlign": "left",
                                            "padding": "4px 16px",
                                            "fontFamily": "Inter",
                                            "fontSize": "13px",
                                            "whiteSpace": "normal",
                                            "height": "30px",
                                            "lineHeight": "30px",
                                        },
                                        style_cell_conditional=[
                                            {
                                                "if": {"column_id": "metric"},
                                                "width": "75%",
                                                "minWidth": "200px",
                                            },
                                            {
                                                "if": {"column_id": "status"},
                                                "width": "25%",
                                                "minWidth": "100px",
                                            },
                                        ],
                                        style_data={
                                            "backgroundColor": "white",
                                            "borderBottom": "1px solid #f0f0f0",
                                            "height": "30px",
                                            "lineHeight": "30px",
                                        },
                                        style_data_conditional=[
                                            {
                                                "if": {"row_index": "odd"},
                                                "backgroundColor": "#f9f9f9",
                                            },
                                            {
                                                "if": {
                                                    "filter_query": "{is_category} eq true"
                                                },
                                                "backgroundColor": "#2c3e50",
                                                "color": "white",
                                                "fontSize": "15px",
                                                "letterSpacing": "0.7px",
                                                "borderTop": "16px solid white",
                                                "height": "44px",
                                                "lineHeight": "44px",
                                                "textTransform": "none",
                                                "fontWeight": "600",
                                            },
                                            {
                                                "if": {
                                                    "filter_query": "{is_category} eq true",
                                                    "column_id": "metric",
                                                },
                                                "textAlign": "left",
                                                "paddingLeft": "16px",
                                            },
                                            {
                                                "if": {
                                                    "filter_query": "{is_category} eq true",
                                                    "column_id": "status",
                                                },
                                                "backgroundColor": "#2c3e50",
                                            },
                                            {
                                                "if": {
                                                    "filter_query": '{status} contains "Yes"',
                                                    "column_id": "status",
                                                },
                                                "color": "#047857",
                                            },
                                            {
                                                "if": {
                                                    "filter_query": '{status} contains "No"',
                                                    "column_id": "status",
                                                },
                                                "color": "#dc2626",
                                            },
                                        ],
                                        page_size=22,
                                        page_action="native",
                                        sort_action="native",
                                        sort_mode="single",
                                        merge_duplicate_headers=True,
                                    ),
                                ],
                                style={
                                    "flex": "0 0 28%",
                                    "backgroundColor": "white",
                                    "padding": "16px",
                                    "borderRadius": "4px",
                                    "boxShadow": "0 1px 3px rgba(0,0,0,0.12)",
                                    "minWidth": "340px",
                                    "maxWidth": "400px",
                                },
                            ),
                            # Right side - Chart (75% width)
                            html.Div(
                                [
                                    html.H2(
                                        "Energy Consumption Over Time",
                                        className="section-title",
                                        style={
                                            "fontFamily": "Inter",
                                            "fontWeight": "500",
                                            "fontSize": "18px",
                                            "marginBottom": "10px",
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
                                    "flex": "1",  # Takes remaining space
                                    "backgroundColor": "white",
                                    "padding": "16px",
                                    "borderRadius": "4px",
                                    "boxShadow": "0 1px 3px rgba(0,0,0,0.12)",
                                },
                            ),
                        ],
                        style={
                            "display": "flex",
                            "gap": "16px",
                            "marginBottom": "24px",
                        },
                    ),
                ],
                style={
                    "maxWidth": "1600px",
                    "margin": "0 auto",
                    "padding": "8px",
                },
            ),
        ]
    )

    return create_base_layout(content)
