from dash import html
import dash_bootstrap_components as dbc
from layouts.base_layout import create_base_layout
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
                className="p-2 fade-in"  # Add animation class
            )
            for page_title, page_info in pages_dict.items()
        ],
        className="flex-wrap justify-content-start g-0",
        style={
            'margin': '0',
            'background': '#f8f9fa',  # Light background
            'borderRadius': '8px',
            'padding': '20px'
        })
    ], className="mb-5")

def create_home_page():
    menu_config = load_menu_config()
    site_config = menu_config.get('site_config', {})
    
    content = html.Div([
        # Site Header with Icon above title
        html.Div([
            # Icon centered above title
            html.Div([
                html.Img(
                    src=site_config.get('header_logo', 'assets/icon.png'),
                    style={'height': '80px', 'marginBottom': '15px'}
                ),
            ], className="text-center"),
            # Title
            html.H1(
                site_config.get('title', 'Data Center Energy Monitor'),
                className="text-center",
                style={'fontFamily': 'Poppins, sans-serif'}
            )
        ], className="my-5"),

        # Sections container with responsive margins
        html.Div([
            *[create_section(category, pages) 
              for category, pages in menu_config.items() 
              if category != 'site_config'],
        ], className="container-fluid px-2 px-sm-3 px-md-4 px-lg-5", 
           style={'maxWidth': '1400px'}),  # Added comma here

        # Back to Top button
        html.Button(
            "↑",
            id="back-to-top",
            className="back-to-top-btn",
            style={
                'position': 'fixed',
                'bottom': '20px',
                'right': '20px',
                'display': 'none',
                'borderRadius': '50%',
                'width': '40px',
                'height': '40px',
                'backgroundColor': '#007bff',
                'color': 'white',
                'border': 'none',
                'cursor': 'pointer',
                'zIndex': 1000
            }
        )
    ])

    return create_base_layout(content)
