from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import pandas as pd

def create_gp_tab4(app, gp_base_df):

    # preprocess data
    policy_group = [
                "Version",
                "Order Type",
                "Status",
                "Date Of Status",
    ]

    policy_timeline_group = [                
                "Date Introduced",
                "Date Of Amendment",
                "Date Enacted",
                "Date In Effect",
                "Date Killed"]
    
    author_group = [
                "Authors",
                "Offices Held"
    ]

    location_group = [
                "Region",
                "Supranational Policy Area",
                "Country",
                "State/Province",
                "County",
                "City",
    ]

    instruments_group = [
            "Measurement and Reporting",
            "Procurement standard",
            "Performance standard",
            "Research, demonstration, and development",
            "Capacity building",
            "Rate structuring",
            "Development incentives",
            "Development restrictions",
            "Other",
        ]

    objectives_group = [
            "Energy",
            "Power",
            "Water",
            "Emissions",
            "Other Environemental",
            "Taxes",
            "Permits",
            "Employement",
            "Communities",
        ]
    

    gp_base_df['total_instruments'] = (gp_base_df[instruments_group] == 'Yes').sum(axis=1)
    gp_base_df['total_objectives'] = (gp_base_df[objectives_group] == 'Yes').sum(axis=1)

    columnDefs = [
        {"field": "Policy Name/Number", "wrapHeaderText": True,"autoHeaderHeight": True,"width": 180},
        *[{"field": policy,"wrapHeaderText": True,"autoHeaderHeight": True,"width": 140}
           for policy in policy_group],
        {
            "headerName": "Author Details",
            "marryChildren": True,
            "children": [
                {"field":"Authors", "headerName": "Author(s)", "columnGroupShow": "closed"},
                *[{"field": author, "columnGroupShow": "open"} for author in author_group]
            ],
        },
        {
            "headerName": "Policy Timeline",
            "marryChildren": True,
            "children": [
                {"field":"Date Introduced", "width": 180, "columnGroupShow": "closed"},
                *[{"field": date, "width": 180, "columnGroupShow": "open"} for date in policy_timeline_group]
            ],
        },
        {"field":"Jurisdiction Level","wrapHeaderText": True,"autoHeaderHeight": True, "width": 140},
        {
            "headerName": "Geographic Scope",
            "marryChildren": True,
            "children": [
                {"field":"Region", "columnGroupShow": "closed", "width": 160},
                *[{"field": location, "columnGroupShow": "open", "width": 140} for location in location_group]
            ],
        },
        {
            "headerName": "Objectives",
            "marryChildren": True,
            "children": [
                {"field":"total_instruments", "headerName": "Total Addressed", 'filter': False,"columnGroupShow": "closed", "width": 140},
                *[{"field": objective, "columnGroupShow": "open","wrapHeaderText": True,"autoHeaderHeight": True,}
                   for objective in objectives_group]
            ],
        },
        {
            "headerName": "Instruments",
            "marryChildren": True,
            "children": [
                {"field":"total_objectives", "headerName": "Total Applied", 'filter': False,"columnGroupShow": "closed","width": 140},
                *[{"field": instrument, "columnGroupShow": "open","wrapHeaderText": True,"autoHeaderHeight": True,}
                   for instrument in instruments_group]
            ],
        },
        {
        "field": "Source",
        "cellRenderer": "markdown",
        "linkTarget": "_blank"
    }
    ]

    row_data = gp_base_df.to_dict("records")

    content = html.Div(
        dag.AgGrid(
            id="gp-tab4-grid",
            rowData=row_data,
            columnDefs=columnDefs,
            defaultColDef={"resizable": True, "sortable": True, "filter": True},
            style={"height": "700px", "padding": "5px 15px 10px 15px"},
            dashGridOptions={
            "theme": "themeBalham",
        },
        ),
    )

    return content