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
    site_config = menu_structure.get('site_config', {})
    navbar_items = menu_structure.get('navbar', {}).get('main', {})

    nav_links = generate_nav_links(navbar_items)

    return html.Nav(
        className="navbar navbar-expand-lg navbar-dark bg-dark",
        children=[
            html.Div(
                className="container-fluid d-flex align-items-center justify-content-between",
                children=[
                    # Left group: hamburger + logo
                    html.Div(
                        className="d-flex align-items-center",
                        style={"marginLeft": "30px"},
                        children=[
                            dbc.NavbarToggler(id="navbar-toggler", className="me-2"),
                            html.A(
                                html.Img(
                                    src=site_config.get('navbar_logo', 'assets/isalab-logo.png'),
                                    className="img-fluid",
                                    style={'maxHeight': '70px'} #45
                                ),
                                className="navbar-brand mb-0 h1",
                                href="/"
                            )
                        ]
                    ),

                    # Right-aligned collapse menu
                    dbc.Collapse(
                        id="navbar-collapse",
                        is_open=False,
                        navbar=True,
                        style={"marginRight": "45px"},
                        # className= "position-absolute translate-middle-x", #"justify-content-center",
                        #className="justify-content-center w-100",
                        children=[
                            dbc.Nav(nav_links, navbar=True), #className="ms-auto"
                        ]
                    )
                ]
            )
        ]
    )

def generate_nav_links(items, parent_label=None):
    nav_links = []

    for label, content in items.items():
        if isinstance(content, dict):
            # If this level has a route, treat as a link
            if "route" in content:
                link_label = f"{parent_label} / {label}" if parent_label else label
                nav_links.append(
                    dbc.NavItem(dbc.NavLink(link_label, href=content["route"]))
                )
            else:
                # Nested items: flatten into dropdown menu
                dropdown_items = []
                for sub_label, sub_content in content.items():
                    if isinstance(sub_content, dict) and "route" in sub_content:
                        dropdown_items.append(
                            dbc.DropdownMenuItem(sub_label, href=sub_content["route"])
                        )
                    elif isinstance(sub_content, dict):
                        # Third-level nesting
                        for subsub_label, subsub_content in sub_content.items():
                            if isinstance(subsub_content, dict) and "route" in subsub_content:
                                combined_label = f"{sub_label} / {subsub_label}"
                                dropdown_items.append(
                                    dbc.DropdownMenuItem(combined_label, href=subsub_content["route"])
                                )

                if dropdown_items:
                    nav_links.append(
                        dbc.DropdownMenu(
                            label=label,
                            nav=True,
                            in_navbar=True,
                            children=dropdown_items
                        )
                    )
    return nav_links