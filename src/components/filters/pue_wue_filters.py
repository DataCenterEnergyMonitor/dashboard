import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc


def create_filters(df):
    return html.Div(
                dbc.Accordion(
                    [
                        dbc.AccordionItem(
                            [
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.H5("Facility Scope"),
                                                        dcc.Checklist(
                                                            id="facility_scope", 
                                                            options=df["facility_scope"].unique(),
                                                            inline=False,
                                                        ),
                                                    ],
                                                    width=2,
                                                    style={
                                                            "padding": "15px", 
                                                            #"backgroundColor": "#f8f9fa", 
                                                            "border": "1px solid #babdc0", 
                                                            "borderRadius": "5px",
                                                            "margin": "5px"
                                                        },
                                                ),
                                                dbc.Col(
                                                    [
                                                        html.H5("Time period category"),
                                                        dcc.Checklist(
                                                            id="facility_scope", 
                                                            options=["Monthly PUE",
                                                                    "Quarterly PUE",
                                                                    "Biannual PUE",
                                                                    "Annual PUE",
                                                                    "Not evident"],
                                                            inline=False,
                                                        ),
                                                    ],
                                                    width=2,
                                                    style={
                                                            "padding": "15px", 
                                                            #"backgroundColor": "#f8f9fa", 
                                                            "border": "1px solid #babdc0", 
                                                            "borderRadius": "5px",
                                                            "margin": "5px"
                                                        },
                                                ),
                                                dbc.Col(
                                                    [
                                                        html.H5("Measurement category"),
                                                        dcc.Checklist(
                                                            id="measurement_category", 
                                                            options=["Category 1",
                                                                    "Category 2",
                                                                    "Category 3",
                                                                    "Not evident"],
                                                            inline=False,
                                                        ),
                                                    ],
                                                    width=2,
                                                        style={
                                                            "padding": "15px", 
                                                            #"backgroundColor": "#f8f9fa", 
                                                            "border": "1px solid #babdc0", 
                                                            "borderRadius": "5px",
                                                            "margin": "5px"
                                                        },
                                                ),
                                            ],
                                        ),
                                        html.Br(),
                                        dbc.Row(
                                            dbc.Col(
                                                [
                                                    html.H5("Region"),
                                                    dcc.Dropdown(
                                                        id="iea_region",
                                                        options=df["iea_region"].unique(),
                                                        value=df["iea_region"][0],
                                                        multi=True,
                                                    ),
                                                ],
                                                width=6
                                            ),
                                        )
                                    ]
                                )
                            ],
                            title="Filters",    
                        )
                    ],
                    flush=True,
                    start_collapsed=True
                ),
            )