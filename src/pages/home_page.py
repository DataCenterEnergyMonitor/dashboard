from dash import html
import dash_bootstrap_components as dbc
from components.navbar import create_navbar
import yaml
import os

def load_menu_config():
    """Load menu configuration from YAML file"""
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'menu_structure.yaml')
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

# Load menu configuration
PAGES = load_menu_config()

def create_section_divider(title):
    """Create a styled section divider"""
    return html.Div([
        dbc.Row([
            dbc.Col(
                html.H2(title, style={'color': '#343a40'}), # section title color: green 14AE5C   
                width="auto",
                className="px-2"
            ),
            dbc.Col(html.Hr(style={'borderColor': '#343a40'}), className="my-auto") # divider line color: green 14AE5C
        ], align="center", className="my-3")
    ])

def create_card(title, page_info):
    """Create a card component with preview image"""
    return html.A(  # Wrap entire card in an anchor tag
        dbc.Card([
            dbc.CardImg(
                src=page_info['preview'],
                top=True,
                style={
                    'height': '160px',
                    'objectFit': 'cover'
                }
            ),
            dbc.CardBody([
                html.H5(title, className="card-title"),
                html.P(
                    page_info['description'], 
                    className="card-text small",
                    style={'height': '48px', 'overflow': 'hidden'}  # Fixed height for description
                )
            ])
        ], 
        className="h-100 shadow-sm",  # Make all cards same height with subtle shadow
        style={'width': '300px'}
        ),
        href=page_info['route'],
        style={'textDecoration': 'none'},  # Remove underline from links
        className="p-2"  # Changed from m-3 to p-2 to prevent margin collapse
    )

def create_section(title, pages_dict):
    """Create a section with cards for each page"""
    return html.Div([
        create_section_divider(title),
        dbc.Row([
            dbc.Col(
                create_card(page_title, page_info),
                width="auto",
                className="p-2"  # Added padding to Col
            )
            for page_title, page_info in pages_dict.items()
        ], 
        className="flex-wrap justify-content-start g-0",  # Changed g-2 to g-0 since we're using padding
        style={'margin': '0'}
        )
    ], className="mb-5")

def create_home_page():
    menu_config = load_menu_config()
    site_config = menu_config.get('site_config', {})
    
    return html.Div([
        # Navigation Bar
        create_navbar(),
        
        # Main Content
        html.Div([
            # Site Header with Icon above title
            html.Div([
                # Icon centered above title
                html.Div([
                    html.Img(
                        src=site_config.get('header_logo', 'assets/icon.png'),
                        style={'height': '80px', 'marginBottom': '15px'}  # Added bottom margin
                    ),
                ], className="text-center"),
                # Title
                html.H1(
                    site_config.get('title', 'Data Center Energy Monitor'),
                    className="text-center"
                )
            ], className="my-5"),

            # # Description
            # dbc.Card(
            #     dbc.CardBody([
            #         html.P(
            #             "Welcome to the Data Center Analytics Dashboard. "
            #             "This platform provides comprehensive insights into data center energy reporting metrics.",
            #             className="lead text-center mb-0"
            #         )
            #     ]),
            #     className="mb-5",
            #     style={'borderColor': '#14AE5C'}  # Custom green border
            # ),

            # Sections
            *[create_section(category, pages) 
              for category, pages in menu_config.items() 
              if category != 'site_config'],

            # Footer
            html.Footer([
                html.Hr(className="mt-5"),
                html.P(
                    "© 2024 Data Center Energy Monitor. All rights reserved.",
                    className="text-center text-muted"
                )
            ], className="mt-5")
            
        ], className="container py-4")
    ])
