import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc


def create_energy_projections_filters(df):
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
                            # Study
                            html.Div(
                                [
                                    # html.H5(
                                    #     "Study",
                                    #     className="filter-section-title",
                                    #     style={
                                    #         "color": "#34495e",
                                    #         "fontSize": "1.1rem",
                                    #         "fontWeight": "600",
                                    #         "marginBottom": "15px",
                                    #         "marginTop": "20px",
                                    #     },
                                    # ),
                                    html.Label("Units:", className="filter-label",
                                               style={'margin-top': '15px'}),
                                    dcc.RadioItems(
                                        id="units",
                                        # options=[
                                        #     {"label": val, "value": val}
                                        #     for val in sorted(df["citation"].unique())
                                        # ],
                                        options=['TWh', 'GW'],
                                        value='TWh',
                                        inline=True,
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box horizontal-checklist mb-3",
                                        labelStyle={"display": "inline-block", "margin-right": "10px"},
                                    ), 

                                    html.Label("Citation:", className="filter-label"),
                                    dcc.Dropdown(
                                        id="citation",
                                        # options=[
                                        #     {"label": val, "value": val}
                                        #     for val in sorted(df["citation"].unique())
                                        # ],
                                        options=[],
                                        multi=True,
                                        persistence=True,
                                        persistence_type="session",
                                        placeholder="Select studies",
                                        className="filter-box mb-3",
                                    ),
                                    html.Label(
                                        "Publication Year:", className="filter-label"
                                    ),
                                    dcc.Dropdown(
                                        id="year_of_publication",
                                        options=[],
                                        multi=True,
                                        persistence=True,
                                        persistence_type="session",
                                        placeholder="Select publication year",
                                        className="filter-box mb-3",
                                    ),
                                    html.Label(
                                        "Publisher institution type(s):",
                                        className="filter-label",
                                    ),
                                    dcc.Dropdown(
                                        id="publisher_institution_type_s_",
                                        options=[],
                                        multi=True,
                                        persistence=True,
                                        persistence_type="session",
                                        placeholder="Select publisher institution types",
                                        className="filter-box mb-3",
                                    ),
                                    html.Label(
                                        "Author institution type(s):",
                                        className="filter-label",
                                    ),
                                    dcc.Dropdown(
                                        id="author_institution_type_s_",
                                        options=sorted(df["citation"].unique()),
                                        multi=True,
                                        persistence=True,
                                        persistence_type="session",
                                        placeholder="Select author institution types",
                                        className="filter-box mb-3",
                                    ),
                                    html.Label(
                                        "Study Region:", className="filter-label"
                                    ),
                                    dcc.Dropdown(
                                        id="study_region",
                                        options=[],
                                        multi=True,
                                        placeholder="Select study region(s)",
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box mb-2",
                                    ),
                                    html.Label(
                                        "Data center type(s):", className="filter-label"
                                    ),
                                    dcc.Dropdown(
                                        id="data_center_type_s_",
                                        options=[],
                                        multi=True,
                                        placeholder="Select data center type(s)",
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box mb-2",
                                    ),
                                    html.Label(
                                        "Associated granularity:",
                                        className="filter-label",
                                    ),
                                    dcc.Dropdown(
                                        id="associated_granularity",
                                        options=[],
                                        multi=True,
                                        placeholder="Select granularity",
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box mb-2",
                                    ),
                                    html.Label(
                                        "Modeling approach(es):",
                                        className="filter-label",
                                    ),
                                    dcc.Dropdown(
                                        id="modeling_approach_es_",
                                        options=[],
                                        multi=True,
                                        placeholder="Select modeling approache(s)",
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box mb-2",
                                    ),
                                    html.Label(
                                        "Input data type(s):", className="filter-label"
                                    ),
                                    dcc.Dropdown(
                                        id="input_data_type_s_",
                                        options=[],
                                        multi=True,
                                        placeholder="Select input data type(s)",
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box mb-2",
                                    ),
                                    html.Label(
                                        "Time horizon:", className="filter-label"
                                    ),
                                    dcc.Dropdown(
                                        id="time_horizon",
                                        options=[],
                                        multi=True,
                                        placeholder="Select time horizon",
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box mb-2",
                                    ),
                                    html.Label(
                                        "Projection narrative:",
                                        className="filter-label",
                                    ),
                                    dcc.Dropdown(
                                        id="projection_narrative_s_",
                                        options=[],
                                        multi=True,
                                        placeholder="Select projection narrative",
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box mb-2",
                                    ),
                                    html.Label("Scenario:", className="filter-label"),
                                    dcc.Dropdown(
                                        id="label",
                                        options=[],
                                        multi=True,
                                        placeholder="Select projection scenario",
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box mb-2",
                                    ),
                                    html.Label(
                                        [
                                            "Overall Quality Rating:",
                                            #    dbc.Tooltip(
                                            #             "1: No peer review or external feedback evident"\
                                            #             "2: Inputs and comments from external experts acknowledged, but not framed as peer review" \
                                            #             "3: Peer-reviewed journal; peer-review explicitly acknowledged, whether reviewers named or anonymous",
                                            #             target="peer-review-tooltip",
                                            #             placement="right"
                                            #         ),
                                            #     html.I(
                                            #     className="fas fa-info-circle ms-1",
                                            #     id="peer-review-tooltip",
                                            #     style={"fontSize": "12px", "cursor": "help", "color": "#007bff"},
                                            # )
                                        ],
                                        className="filter-label",
                                    ),
                                    html.Div(
                                        dcc.RangeSlider(
                                            id="total_quality_rating",
                                            min=12,
                                            max=36,
                                            value=[12, 36],
                                            persistence=True,
                                            persistence_type="session",
                                            className="filter-box slider-wrapper mb-2",
                                        ),
                                    ),
                                ],
                            ),
                            # Quality Ratings Details Section
                            html.Div(
                                [
                                    html.H5(
                                        "Quality Ratings",
                                        className="filter-section-title",
                                        style={
                                            "color": "#34495e",
                                            "fontSize": "1.1rem",
                                            "fontWeight": "600",
                                            "marginBottom": "15px",
                                            "marginTop": "20px",
                                        },
                                    ),
                                    html.Label(
                                        [
                                            "Peer review:",
                                            dbc.Tooltip(
                                                "1: No peer review or external feedback evident"
                                                "2: Inputs and comments from external experts acknowledged, but not framed as peer review"
                                                "3: Peer-reviewed journal; peer-review explicitly acknowledged, whether reviewers named or anonymous",
                                                target="peer-review-tooltip",
                                                placement="right",
                                            ),
                                            html.I(
                                                className="fas fa-info-circle ms-1",
                                                id="peer-review-tooltip",
                                                style={
                                                    "fontSize": "12px",
                                                    "cursor": "help",
                                                    "color": "#007bff",
                                                },
                                            ),
                                        ],
                                        className="filter-label",
                                    ),
                                    dcc.Checklist(
                                        id="peer_review",
                                        options=["1", "2", "3"],
                                        value=[],
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box horizontal-checklist mb-3",
                                        inline=True,
                                    ),
                                    html.Label(
                                        [
                                            "Model Availability:",
                                            dbc.Tooltip(
                                                "Are equations/code available to replicate results with relevant data inputs?"
                                                "1: Insufficient documentation for model and results replication"
                                                "2: Incomplete availability of equations or model code enabling partial replication of results"
                                                "3: All equations provided in the text (inclusive of supplementary information) and/or via publicly-available code for full results replication",
                                                target="model-availability-tooltip",
                                                placement="right",
                                            ),
                                            html.I(
                                                className="fas fa-info-circle ms-1",
                                                id="model-availability-tooltip",
                                                style={
                                                    "fontSize": "12px",
                                                    "cursor": "help",
                                                    "color": "#007bff",
                                                },
                                            ),
                                        ],
                                        className="filter-label",
                                    ),
                                    dcc.Checklist(
                                        id="model_availability",
                                        options=["1", "2", "3"],
                                        value=[],
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box horizontal-checklist mb-3",
                                        inline=True,
                                    ),
                                    html.Label(
                                        [
                                            "Data Availability:",
                                            dbc.Tooltip(
                                                "Are input data available publicly?"
                                                "1: Few/no input data available publicly"
                                                "2: Some input data available publicly"
                                                "3: All/most input data available publicly",
                                                target="data-availability-tooltip",
                                                placement="right",
                                            ),
                                            html.I(
                                                className="fas fa-info-circle ms-1",
                                                id="data-availability-tooltip",
                                                style={
                                                    "fontSize": "12px",
                                                    "cursor": "help",
                                                    "color": "#007bff",
                                                },
                                            ),
                                        ],
                                        className="filter-label",
                                    ),
                                    dcc.Checklist(
                                        id="data_availability",
                                        options=["1", "2", "3"],
                                        value=[],
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box horizontal-checklist mb-3",
                                        inline=True,
                                    ),
                                    html.Label(
                                        [
                                            "Sensitivity analysis:",
                                            dbc.Tooltip(
                                                "1: No sensitivity analysis or qualitative discussion of variable contributions"
                                                "2: Limited/no sensitivity analysis but qualitative discussion of important variables"
                                                "3: Quantitative sensitivity analysis presented to isolate most important variables",
                                                target="sensitivity-analysis-tooltip",
                                                placement="right",
                                            ),
                                            html.I(
                                                className="fas fa-info-circle ms-1",
                                                id="sensitivity-analysis-tooltip",
                                                style={
                                                    "fontSize": "12px",
                                                    "cursor": "help",
                                                    "color": "#007bff",
                                                },
                                            ),
                                        ],
                                        className="filter-label",
                                    ),
                                    dcc.Checklist(
                                        id="sensitivity_analysis",
                                        options=["1", "2", "3"],
                                        value=[],
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box horizontal-checklist mb-3",
                                        inline=True,
                                    ),
                                    html.Label(
                                        [
                                            "Uncertainty quantification:",
                                            dbc.Tooltip(
                                                "1: No quantitative treatment of uncertainty; only point values presented for results"
                                                "2: Uncertainty quantified for some, but not all, results and/or insufficiently described"
                                                "3: Quantitative uncertainty analysis provided, inclusive of upper/lower values and/or scenarios, for all results with clear descriptions",
                                                target="uncertainty-quantification-tooltip",
                                                placement="right",
                                            ),
                                            html.I(
                                                className="fas fa-info-circle ms-1",
                                                id="uncertainty-quantification-tooltip",
                                                style={
                                                    "fontSize": "12px",
                                                    "cursor": "help",
                                                    "color": "#007bff",
                                                },
                                            ),
                                        ],
                                        className="filter-label",
                                    ),
                                    dcc.Checklist(
                                        id="uncertainty_quantification",
                                        options=["1", "2", "3"],
                                        value=[],
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box horizontal-checklist mb-3",
                                        inline=True,
                                    ),
                                    html.Label(
                                        [
                                            "Analytical rigor:",
                                            dbc.Tooltip(
                                                "to capture if deep discussion of assumptions/approach is offered or casual assumptions"
                                                "1: Limited/no critical discussion/justification of data source(s), modeling approach(s), assumptions, and results"
                                                "2: Some critical discussion/justification of data sources, modeling approaches, assumptions, and results"
                                                "3: Thorough discussion/justification of data source(s), modeling approach(s), assumptions, and results",
                                                target="analytical-rigor-tooltip",
                                                placement="right",
                                            ),
                                            html.I(
                                                className="fas fa-info-circle ms-1",
                                                id="analytical-rigor-tooltip",
                                                style={
                                                    "fontSize": "12px",
                                                    "cursor": "help",
                                                    "color": "#007bff",
                                                },
                                            ),
                                        ],
                                        className="filter-label",
                                    ),
                                    dcc.Checklist(
                                        id="analytical_rigor",
                                        options=["1", "2", "3"],
                                        value=[],
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box horizontal-checklist mb-3",
                                        inline=True,
                                    ),
                                    html.Label(
                                        [
                                            "Results validation:",
                                            dbc.Tooltip(
                                                'Does analysis "ground truth" its results by comparing to other values or performing reality checks'
                                                "1: No comparisions/discussions of results in context of any previous work or available validation data"
                                                "2: Comparisons/discussions of results in context of limited body of previous work and/or available validation data"
                                                "3: Comparisons/discussions of results in context of comprehensive body of previous work and/or available validation data",
                                                target="results-validation-tooltip",
                                                placement="right",
                                            ),
                                            html.I(
                                                className="fas fa-info-circle ms-1",
                                                id="results-validation-tooltip",
                                                style={
                                                    "fontSize": "12px",
                                                    "cursor": "help",
                                                    "color": "#007bff",
                                                },
                                            ),
                                        ],
                                        className="filter-label",
                                    ),
                                    dcc.Checklist(
                                        id="results_validation",
                                        options=["1", "2", "3"],
                                        value=[],
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box horizontal-checklist mb-3",
                                        inline=True,
                                    ),
                                    html.Label(
                                        [
                                            "Granularity:",
                                            dbc.Tooltip(
                                                "How detailed is the approach and reporting such that energy demand drivers are isolated and transparent?"
                                                "1: No analysis or reporting at the levels of different data center, IT equipment, and infrastructure equipment types; total data center or total sector only"
                                                "2: Partial analysis or reporting at the levels of different data center, IT equipment, and infrastructure equipment types; e.g., all IT together, all infrastructure together"
                                                "3: Substantial analysis or reporting at the levels of different data center, IT equipment, and infrastructure equipment types",
                                                target="granularity-tooltip",
                                                placement="right",
                                            ),
                                            html.I(
                                                className="fas fa-info-circle ms-1",
                                                id="granularity-tooltip",
                                                style={
                                                    "fontSize": "12px",
                                                    "cursor": "help",
                                                    "color": "#007bff",
                                                },
                                            ),
                                        ],
                                        className="filter-label",
                                    ),
                                    dcc.Checklist(
                                        id="granularity",
                                        options=["1", "2", "3"],
                                        value=[],
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box horizontal-checklist mb-3",
                                        inline=True,
                                    ),
                                    html.Label(
                                        [
                                            "Completeness:",
                                            dbc.Tooltip(
                                                "Does the study 's approach/data correspond to its stated scope?"
                                                "1: Model/data scope omit major elements of stated or reasonably intepreted physical systems scope, with no attempt to fill gaps"
                                                "2: Model/data scope omit minor aspects of stated or reasonably interpreted pyhsical systems scope, with simplified assumptions used to fill gaps"
                                                "3: Model/data scope fully cover stated or reasonably interpreted pyhsical systems scope",
                                                target="completeness-tooltip",
                                                placement="right",
                                            ),
                                            html.I(
                                                className="fas fa-info-circle ms-1",
                                                id="completeness-tooltip",
                                                style={
                                                    "fontSize": "12px",
                                                    "cursor": "help",
                                                    "color": "#007bff",
                                                },
                                            ),
                                        ],
                                        className="filter-label",
                                    ),
                                    dcc.Checklist(
                                        id="completeness",
                                        options=["1", "2", "3"],
                                        value=[],
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box horizontal-checklist mb-3 more-space",
                                        inline=True,
                                    ),
                                    html.Label(
                                        [
                                            "Technological Correlation:",
                                            dbc.Tooltip(
                                                "Data are representative of actual or expected technology types, in the past or future"
                                                "1: To be defined"
                                                "2: To be defined"
                                                "3: To be defined",
                                                target="technological-correlation-tooltip",
                                                placement="right",
                                            ),
                                            html.I(
                                                className="fas fa-info-circle ms-1",
                                                id="technological-correlation-tooltip",
                                                style={
                                                    "fontSize": "12px",
                                                    "cursor": "help",
                                                    "color": "#007bff",
                                                },
                                            ),
                                        ],
                                        className="filter-label",
                                    ),
                                    dcc.Checklist(
                                        id="technology_correlation",
                                        options=["1", "2", "3"],
                                        value=[],
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box horizontal-checklist mb-3",
                                        inline=True,
                                    ),
                                    html.Label(
                                        [
                                            "Geographical Correlation:",
                                            dbc.Tooltip(
                                                "Data are representative of technology performance in the region(s) of study, in the past or future"
                                                "1: To be defined"
                                                "2: To be defined"
                                                "3: To be defined",
                                                target="geographical-correlation-tooltip",
                                                placement="right",
                                            ),
                                            html.I(
                                                className="fas fa-info-circle ms-1",
                                                id="geographical-correlation-tooltip",
                                                style={
                                                    "fontSize": "12px",
                                                    "cursor": "help",
                                                    "color": "#007bff",
                                                },
                                            ),
                                        ],
                                        className="filter-label",
                                    ),
                                    dcc.Checklist(
                                        id="geographical_correlation",
                                        options=["1", "2", "3"],
                                        value=[],
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box horizontal-checklist mb-3",
                                        inline=True,
                                    ),
                                    html.Label(
                                        [
                                            "Temporal Correlation:",
                                            dbc.Tooltip(
                                                "Data are representative of technological change expected over analyzed time horizons"
                                                "1: To be defined"
                                                "2: To be defined"
                                                "3: To be defined",
                                                target="temporal-correlation-tooltip",
                                                placement="right",
                                            ),
                                            html.I(
                                                className="fas fa-info-circle ms-1",
                                                id="temporal-correlation-tooltip",
                                                style={
                                                    "fontSize": "12px",
                                                    "cursor": "help",
                                                    "color": "#007bff",
                                                },
                                            ),
                                        ],
                                        className="filter-label",
                                    ),
                                    dcc.Checklist(
                                        id="temporal_correlation",
                                        options=["1", "2", "3"],
                                        value=[],
                                        persistence=True,
                                        persistence_type="session",
                                        className="filter-box horizontal-checklist mb-3",
                                        inline=True,
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
                                        id="apply-filters-btn",
                                        color="primary",
                                        size="sm",
                                        n_clicks=0,
                                        className="mb-2",
                                        style={"width": "100%", "borderRadius": "5px"},
                                    ),
                                    dbc.Button(
                                        "Clear All",
                                        id="clear-filters-btn",
                                        color="outline-secondary",
                                        size="sm",
                                        n_clicks=0,
                                        style={"width": "100%", "borderRadius": "5px"},
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
                    # "backgroundColor": "#f8f9fa",
                    "borderRight": "1px solid #dee2e6",
                    "padding": "20px",
                    "zIndex": "999",  # Lower than navbar but higher than content
                    # "boxShadow": "2px 0 5px rgba(0,0,0,0.1)",
                    # "overflowY": "auto"
                },
            )
        ]
    )


def get_options(column, filtered_df):
    """Get unique options from filtered dataframe"""
    return [
        {"label": val, "value": val} for val in sorted(filtered_df[column].unique())
    ]
