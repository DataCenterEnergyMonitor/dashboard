from dash import html, dash_table
import dash_bootstrap_components as dbc
from dash_bootstrap_components import icons


def create_category_section(title, data):
    return html.Div(
        [
            dbc.Button(
                [
                    html.I(
                        className="fas fa-chevron-down me-2",
                        id=f"chevron-{title.lower().replace(' ', '-')}",
                        style={"width": "12px", "paddingRight": "20px"},
                    ),
                    title,
                ],
                id=f"collapse-button-{title.lower().replace(' ', '-')}",
                className="category-button d-flex align-items-center",
                style={
                    "backgroundColor": "#00588D",
                    "color": "white",
                    "border": "none",
                    "width": "100%",
                    "textAlign": "left",
                    "padding": "5px 16px",
                    "marginBottom": "1px",
                    "fontSize": "15px",
                    "letterSpacing": "0.7px",
                    "fontWeight": "500",
                    "fontFamily": "Inter",
                },
            ),
            dbc.Collapse(
                dash_table.DataTable(
                    id=f"table-{title.lower().replace(' ', '-')}",
                    columns=[
                        {"name": "REPORTING METRIC", "id": "metric"},
                        {"name": "STATUS", "id": "status"},
                    ],
                    data=data,
                    style_table={
                        "overflowY": "hidden",
                        "overflowX": "hidden",
                        "width": "100%",
                    },
                    style_header={
                        "backgroundColor": "#FFFFFF !important",
                        "fontWeight": "500",
                        "fontFamily": "Inter",
                        "fontSize": "13px",
                        "color": "#374151",
                        "borderBottom": "2px solid #e5e7eb",
                    },
                    style_cell={
                        "textAlign": "left",
                        "padding": "4px 10px",
                        "fontFamily": "Inter",
                        "fontSize": "13px",
                        "whiteSpace": "normal",
                        "height": "30px",
                        "lineHeight": "30px",
                    },
                    style_cell_conditional=[
                        {
                            "if": {"column_id": "metric"},
                            "width": "80%",
                            "minWidth": "200px",
                        },
                        {
                            "if": {"column_id": "status"},
                            "width": "20%",
                            "minWidth": "80px",
                        },
                    ],
                    style_data={
                        "backgroundColor": "white",
                        "borderBottom": "1px solid #f0f0f0",
                    },
                    style_data_conditional=[
                        {
                            "if": {"row_index": "odd"},
                            "backgroundColor": "#f9f9f9",
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
                    sort_action="native",
                    sort_mode="single",
                ),
                id=f"collapse-{title.lower().replace(' ', '-')}",
                is_open=True,
            ),
        ],
        style={"marginBottom": "8px"},
    )
