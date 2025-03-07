from dash import html
import dash_bootstrap_components as dbc
import yaml
import os

def load_menu_config():
    """Load menu configuration from YAML file"""
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'menu_structure.yaml')
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def create_navbar():
    menu_structure = load_menu_config()
    site_config = menu_structure.pop('site_config', {})  # Remove site_config from menu_structure
    
    return html.Nav(
        className="navbar navbar-expand-lg navbar-dark bg-dark",
        children=[
            html.Div(
                className="container-fluid",
                children=[
                    # Use navbar_logo from site_config
                    html.A(
                        html.Img(
                            src=site_config.get('navbar_logo', 'assets/isalab-logo.png'),
                            height="30px",
                            style={'objectFit': 'contain'}
                        ),
                        className="navbar-brand",
                        href="/"
                    ),
                    
                    # Navbar Toggle Button
                    dbc.NavbarToggler(id="navbar-toggler"),
                    
                    # Navbar Content
                    dbc.Collapse(
                        id="navbar-collapse",
                        is_open=False,
                        navbar=True,
                        children=[
                            dbc.Nav([
                                dbc.NavItem(dbc.NavLink("Home", href="/")),
                                dbc.NavItem(dbc.NavLink("About", href="/about")),
                                
                                # Dynamic Dropdowns from YAML config
                                *[
                                    dbc.DropdownMenu(
                                        label=category,
                                        nav=True,
                                        children=[
                                            dbc.DropdownMenuItem(
                                                title,
                                                href=info['route']
                                            )
                                            for title, info in pages.items()
                                            if isinstance(info, dict)  # Ensure we only process page entries
                                        ]
                                    )
                                    for category, pages in menu_structure.items()
                                ],
                            ], navbar=True)
                        ]
                    )
                ]
            )
        ]
    )