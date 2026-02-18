import dash_ag_grid as dag
from dash import html

# Mapping between raw data values and polished display values
METRIC_MAPPING = {
    "Total company electricity use reporting?": "Company-wide Electricity Usage",
    "Total data center fleet electricity use reporting?": "Data Center Fleet Electricity Usage",
    "Individual data center electricity use reporting?": "Individual Data Center Electricity Usage",
    "Data center fuel use reporting?": "Data Center Fuel Usage",
    "PUE reporting?": "Power Usage Effectiveness (PUE)",
    "Total company water use reporting?": "Company-wide Water Usage",
    "Total data center fleet water use reporting?": "Data Center Fleet Water Usage",
    "Individual data center water use reporting?": "Individual Data Center Water Usage",
    "WUE reporting?": "Water Usage Effectiveness (WUE)",
    "Total company electric power sources reporting?": "Company-wide Power Sources",
    "Data center fleet electric power sources reporting?": "Data Center Fleet Power Sources",
    "Individual data center electric power sources reporting?": "Individual Data Center Power Sources",
    "Third-party standards utilization?": "CDP Reporting",
    "Total company Scope 1 GHG reporting?": "Company-wide Scope 1 Emissions",
    "Data center fleet Scope 1 GHG reporting?": "Data Center Fleet Scope 1 Emissions",
    "Individual data center Scope 1 GHG reporting?": "Individual Data Center Scope 1 Emissions",
    "Total company Scope 2 GHG reporting?": "Company-wide Scope 2 Emissions",
    "Data center fleet Scope 2 GHG reporting?": "Data Center Fleet Scope 2 Emissions",
    "Individual data center Scope 2 GHG reporting?": "Individual Data Center Scope 2 Emissions",
    "Total company Scope 3 GHG reporting?": "Company-wide Scope 3 Emissions",
    "Data center fleet Scope 3 GHG reporting?": "Data Center Fleet Scope 3 Emissions",
    "Individual data center Scope 3 GHG reporting?": "Individual Data Center Scope 3 Emissions",
}

# Metrics organised by category (using raw data values).
METRIC_CATEGORIES = {
    "Energy Reporting": [
        "Total company electricity use reporting?",
        "Total data center fleet electricity use reporting?",
        "Individual data center electricity use reporting?",
        "Data center fuel use reporting?",
        "PUE reporting?",
    ],
    "Water Reporting": [
        "Total company water use reporting?",
        "Total data center fleet water use reporting?",
        "Individual data center water use reporting?",
        "WUE reporting?",
    ],
}

# ── Column definitions (shared by every category grid) ──────────────────

_COLUMN_DEFS = [
    {
        "field": "metric",
        "headerName": "Reporting Metric",
        "width": 460,
    },
    {
        "field": "status",
        "headerName": "Status",
        "width": 100,
        "cellStyle": {
            "styleConditions": [
                {
                    "condition": "params.value === 'Yes'",
                    "style": {"color": "#047857", "fontWeight": "600"},
                },
                {
                    "condition": "params.value === 'No'",
                    "style": {"color": "#dc2626", "fontWeight": "600"},
                },
            ],
        },
    },
]

_DEFAULT_COL_DEF = {
    "resizable": True,
    "sortable": False,
}


def build_category_rows(table_df, metrics):
    """Return a list of row dicts for a single category.

    Parameters
    ----------
    table_df : DataFrame
        dataframe with ``metric`` and ``status`` columns filtered by company.
    metrics : list[str]
        Raw metric keys for this category.
    """
    rows = []
    for metric in metrics:
        metric_row = table_df[table_df["metric"] == metric]
        if not metric_row.empty:
            raw_status = metric_row.iloc[0]["status"]
            status = "Yes" if raw_status in ["Y", "y"] else "No"
        else:
            status = "—"
        rows.append(
            {
                "metric": METRIC_MAPPING.get(metric, metric),
                "status": status,
            }
        )
    return rows


def create_reporting_profile_grid(grid_id, row_data):
    """Return a single AG Grid per each metric category.

    Parameters
    ----------
    grid_id : str
        Unique component id for this grid (e.g. ``"cp-grid-energy"``).
    row_data : list[dict]
        Rows with ``metric`` and ``status`` keys.
    """
    return dag.AgGrid(
        id=grid_id,
        className="cp-reporting-profile-grid",
        rowData=row_data,
        columnDefs=_COLUMN_DEFS,
        defaultColDef=_DEFAULT_COL_DEF,
        dashGridOptions={
            "theme": "themeAlpine",
            "domLayout": "autoHeight",
            "suppressHorizontalScroll": True,
        },
    )


def create_reporting_profile_section(table_df):
    """Build the full reporting-profile section: one grid per category.

    Parameters
    ----------
    table_df : DataFrame
        Already filtered to the selected company.

    Returns
    -------
    html.Div
        Contains a category heading + AG Grid for each entry in
        ``METRIC_CATEGORIES``.
    """
    children = []
    for idx, (category, metrics) in enumerate(METRIC_CATEGORIES.items()):
        row_data = build_category_rows(table_df, metrics)
        grid_id = f"cp-grid-{category.lower().replace(' ', '-')}"

        children.append(
            html.Div(
                [
                    html.H6(
                        category,
                        style={
                            "fontFamily": "Inter, sans-serif",
                            "fontWeight": "600",
                            "fontSize": "15px",
                            "color": "#2c3e50",
                            "backgroundColor": "#eef2f7",
                            "padding": "8px 12px",
                            "marginBottom": "0px",
                            "marginTop": "16px" if idx > 0 else "0px",
                            "borderBottom": "1px solid #d1d5db",
                        },
                    ),
                    create_reporting_profile_grid(grid_id, row_data),
                ],
            )
        )

    return html.Div(children, style={"width": "560px", "padding-top":"15px"})
