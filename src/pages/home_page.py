from dash import html
import dash_bootstrap_components as dbc
from layouts.base_layout import create_base_layout
from components.kpi_data_cards import create_kpi_cards
import yaml
import os


def load_menu_config():
    """Load menu configuration from YAML file"""
    config_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "menu_structure.yaml"
    )
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


# Load menu configuration
PAGES = load_menu_config()


def create_section_divider(title):
    """Create a styled section divider"""
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        # html.H2(title, style={'color': '#343a40'}), # section title color: green 14AE5C
                        width="auto",
                        className="px-2",
                    ),
                    dbc.Col(
                        html.Hr(style={"borderColor": "#343a40"}), className="my-auto"
                    ),  # divider line color: green 14AE5C
                ],
                align="center",
                className="my-3",
            )
        ]
    )


def create_card(title, page_info):
    """Create a card component with preview image"""
    return html.A(  # Wrap entire card in an anchor tag
        dbc.Card(
            [
                dbc.CardImg(
                    src=page_info["preview"],
                    top=True,
                    style={
                        "height": "200px",
                        "objectFit": "cover",
                    },  # Increased height from 180px
                ),
                dbc.CardBody(
                    [
                        html.H5(title, className="card-title"),
                        html.P(
                            page_info["description"],
                            className="card-text small",
                            style={
                                "height": "48px",
                                "overflow": "hidden",
                            },  # Fixed height for description
                        ),
                    ]
                ),
            ],
            className="h-100 shadow-sm content-tile",  # Added content-tile class for hover effects
            style={"width": "450px"},  # Increased width from 400px
        ),
        href=page_info["route"],
        style={"textDecoration": "none"},  # Remove underline from links
        className="p-2",  # Changed from m-3 to p-2 to prevent margin collapse
    )


def create_section(title, pages_dict):
    """Create a section with cards for each page"""
    return html.Div(
        [
            # create_section_divider(title),
            dbc.Row(
                html.P(
                    [
                        "Click on the tiles below to explore our datasets ",
                        html.Span(
                            "↓",
                            style={
                                "color": "rgba(64, 64, 64, 0.7)",
                                "fontSize": "1.2em",
                                "marginLeft": "4px",
                            },
                        ),
                        html.Br(),
                        "To review the basics, start with our ",
                        html.A(
                            "Data Center Energy Use 101",
                            href="/energy-101",
                        ),
                        " and ",
                        html.A(
                            "Data Center Water Use 101",
                            href="/water-101",
                        ),
                        " primers. ",
                        html.Br(),
                        "For a current view of the companies we track and our progress, visit ",
                        html.A(
                            "Companies",
                            href="/companies",
                        ),
                    ],
                    className="text-center page-description justify-content-center g-0",
                ),
            ),
            dbc.Row(
                [
                    dbc.Col(
                        create_card(page_title, page_info),
                        width="auto",
                        className="p-2 fade-in",  # Add animation class
                    )
                    for page_title, page_info in pages_dict.items()
                ],
                className="flex-wrap justify-content-center g-0",
            ),
        ],
        className="mb-5",
        style={
            "margin": "0",
            "background": "#fafbfc",  # Light background
            "borderRadius": "8px",
            "padding": "20px",
            "padding-top": "20px",
            "padding-bottom": "50px",
            "margin-top": "20px",
        },
    )


def create_home_page(df=None):
    menu_config = load_menu_config()
    site_config = menu_config.get("site_config", {})

    content = html.Div(
        [
            # Site Header with Icon above title
            html.Div(
                [
                    # Title
                    html.H1(
                        site_config.get("title"),
                        className="text-center landing-page-title",
                    ),
                    # Subtitle
                    html.H2(
                        site_config.get("subtitle"),
                        className="text-center landing-page-description",
                    ),
                    # # Icon centered below title
                    # html.Div(
                    #     [
                    #         html.Img(
                    #             src=site_config.get("header_logo", "assets/icon.png"),
                    #             style={
                    #                 "maxWidth": "150px",
                    #                 "marginBottom": "20px",
                    #                 "marginTop": "20px",
                    #             },
                    #         ),
                    #     ],
                    #     className="img-fluid mx-auto d-block mb-3",
                    #     style={"textAlign": "center"},
                    # ),
                ],
                className="my-4 container px-3",
                style={"maxWidth": "60vw", "margin": "0 auto"},
            ),
            # KPI Cards
            create_kpi_cards(df, menu_config)
            if df is not None
            else html.Div("No data available"),
            # Sections container with responsive margins
            html.Div(
                [
                    *[
                        create_section(category, pages)
                        for category, pages in menu_config.items()
                        if category == "landing_page_cards"
                    ],
                ],
                className="container-fluid px-2 px-sm-3 px-md-4 px-lg-4",
                style={"maxWidth": "1600px", "font-family": "Inter, sans-serif"},
            ),
            # Back to Top button
            html.Button(
                "↑",
                id="back-to-top",
                className="back-to-top-btn",
                style={
                    "position": "fixed",
                    "bottom": "20px",
                    "right": "20px",
                    "display": "none",
                    "borderRadius": "50%",
                    "width": "40px",
                    "height": "40px",
                    "backgroundColor": "#007bff",
                    "color": "white",
                    "border": "none",
                    "cursor": "pointer",
                    "zIndex": 1000,
                },
            ),
        ]
    )

    return create_base_layout(content)
