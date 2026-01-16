import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc


def create_gp_tab3_filters(df):
    return html.Div(
        [
            # Sidebar container
            html.Div(
                [
                    # Header
                    html.Div(
                        [
                            html.Span([html.I(className="fas fa-filter me-2"), ""]),
                        ]
                    ),
                    # Scrollable filter content
                    html.Div(
                        [
                            # Policy Details Section
                            html.Div(
                                [
                                    html.H5(
                                        "Policy Details",
                                        className="filter-section-title",
                                        style={
                                            "color": "#34495e",
                                            "fontSize": "1.1rem",
                                            "fontWeight": "600",
                                            "marginBottom": "15px",
                                            "marginTop": "20px",
                                        },
                                    ),
                                    html.Label("Jurisdiction Level:", className="filter-label"
                                    ),
                                    dcc.Dropdown(
                                        id="gp_jurisdiction_level",
                                        options=[],
                                        multi=True,
                                        placeholder="Select jurisdiction level",
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box mb-2",
                                    ),
                                    html.Label("Order Type:", className="filter-label"),
                                    dcc.Dropdown(
                                        id="gp_tab2_order_type",
                                        options=[],
                                        multi=True,
                                        placeholder="Select order type",
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box mb-2",
                                    ),
                                    html.Label("Status:", className="filter-label"),
                                    dcc.Dropdown(
                                        id="gp_tab2_status",
                                        options=[],
                                        multi=True,
                                        placeholder="Select status",
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box mb-2",
                                    ),
                                    html.Label(
                                        "Instruments:", className="filter-label"
                                    ),
                                    dcc.Checklist(
                                        id="gp_tab2_instrument",
                                        options=[
                                            {"label": str(val), "value": val}
                                            for val in sorted(
                                                df["instrument"].dropna().unique()
                                            )
                                        ]
                                        if "instrument" in df.columns
                                        else [],
                                        value=[],
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box mb-3",
                                    ),
                                    html.Label("Objectives:", className="filter-label"),
                                    dcc.Checklist(
                                        id="gp_tab2_objective",
                                        options=[
                                            {"label": str(val), "value": val}
                                            for val in sorted(
                                                df["objective"].dropna().unique()
                                            )
                                        ]
                                        if "objective" in df.columns
                                        else [],
                                        value=[],
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box mb-3",
                                    ),
                                ]
                            ),
                        ],
                        style={
                            "overflowY": "auto",
                            "maxHeight": "calc(100vh - 200px)",  # Allow scrolling
                            "paddingRight": "10px",
                            "paddingBottom": "50px",
                        },
                    ),
                    # Fixed buttons at bottom
                    html.Div(
                        [
                            dbc.ButtonGroup(
                                [
                                    dbc.Button(
                                        "Apply Filters",
                                        id="gp_tab2_apply-filters-btn",
                                        color="primary",
                                        size="sm",
                                        n_clicks=0,
                                        className="mb-2",
                                        style={
                                            "width": "100%",
                                            "borderRadius": "5px",
                                        },
                                    ),
                                    dbc.Button(
                                        "Clear All",
                                        id="gp_tab2_clear-filters-btn",
                                        color="outline-secondary",
                                        size="sm",
                                        n_clicks=0,
                                        style={
                                            "width": "100%",
                                            "borderRadius": "5px",
                                        },
                                    ),
                                ],
                                vertical=True,
                                className="w-100",
                            )
                        ],
                        style={
                            "position": "sticky",
                            "bottom": "0",
                            "backgroundColor": "#f8f9fa",
                            "padding": "15px 0",
                            "marginTop": "20px",
                            "borderTop": "1px solid #dee2e6",
                        },
                    ),
                    # Hidden div to store applied filter state
                    html.Div(id="applied-filters-store", style={"display": "none"}),
                ],
                style={
                    "width": "300px",
                    "height": "calc(100vh - 100px)",  # Subtract navbar height
                    "position": "fixed",
                    "left": "0",
                    "top": "100px",
                    "borderRight": "1px solid #dee2e6",
                    "padding": "20px",
                    "zIndex": "999",  # Lower than navbar but higher than content
                },
            ),
        ]
    )


def get_options(column, filtered_df):
    """Get unique options from filtered dataframe"""
    return [
        {"label": val, "value": val} for val in sorted(filtered_df[column].unique())
    ]
