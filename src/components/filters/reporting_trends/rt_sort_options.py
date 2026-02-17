"""
Reusable sorting options component for Company Reporting Trends heatmaps.

This component provides dropdown controls for:
- Sort by: company name or reporting status
- Sort order: ascending or descending

Used in tabs 2-5 filter panels.
"""

from dash import dcc, html


def create_sort_options_component(include_status=True):
    """Create sorting options dropdowns.

    Args:
        include_status: If True, includes reporting status as a sort option.
                       Set to False for tabs that don't have status filtering.

    Returns:
        html.Div containing the sort dropdowns
    """
    # Sort by options
    sort_by_options = [
        {"label": "Company Name", "value": "company_name"},
    ]

    if include_status:
        sort_by_options.append({"label": "Reporting Status", "value": "reporting_status"})

    return html.Div(
        [
            html.Label(
                "Sort Options:", className="filter-label", style={"marginTop": "15px"}
            ),
            html.Div(
                [
                    # Sort by dropdown
                    html.Div(
                        [
                            html.Label(
                                "Sort by:",
                                style={
                                    "fontSize": "0.85rem",
                                    "color": "#666",
                                    "marginBottom": "4px",
                                },
                            ),
                            dcc.Dropdown(
                                id="rt-sort-by",
                                options=sort_by_options,
                                value="company_name",
                                clearable=False,
                                persistence=True,
                                persistence_type="session",
                                style={"fontSize": "13px"},
                            ),
                        ],
                        style={"flex": "1", "marginRight": "10px"},
                    ),
                    # Sort order dropdown
                    html.Div(
                        [
                            html.Label(
                                "Order:",
                                style={
                                    "fontSize": "0.85rem",
                                    "color": "#666",
                                    "marginBottom": "4px",
                                },
                            ),
                            dcc.Dropdown(
                                id="rt-sort-order",
                                options=[
                                    {"label": "Low to High", "value": "asc"},
                                    {"label": "High to Low", "value": "desc"},
                                ],
                                value="asc",
                                clearable=False,
                                persistence=True,
                                persistence_type="session",
                                style={"fontSize": "13px"},
                            ),
                        ],
                        style={"flex": "1"},
                    ),
                ],
                style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "flex-start",
                },
            ),
        ],
        className="filter-box mb-3",
    )


def create_hidden_sort_placeholders():
    """Create hidden sort dropdowns for tabs that don't show sort options.

    This ensures callbacks can reference these IDs without errors.
    """
    return html.Div(
        [
            dcc.Dropdown(
                id="rt-sort-by",
                value="company_name",
                style={"display": "none"},
            ),
            dcc.Dropdown(
                id="rt-sort-order",
                value="asc",
                style={"display": "none"},
            ),
        ]
    )
