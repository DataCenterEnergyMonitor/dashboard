import dash_bootstrap_components as dbc
from dash import html, dcc
import yaml
import os

def create_navbar():
    """Create bookmark navigation bar for data-viz pages"""

    menu_structure = load_menu_config()
    navbar_items = menu_structure.get("navbar", {}).get("data_page", {})

    nav_links = generate_nav_links(navbar_items)
    
    return html.Div([
        html.Div([

            # Right-aligned collapse menu
            html.Div(
                dbc.Collapse(
                    id="navbar-collapse",
                    is_open=True,  # Changed to True to make visible
                    navbar=True,
                    className="justify-content-end",
                    children=[
                        dbc.Nav(nav_links, navbar=True, className="ms-auto"),
                    ],
                    style={"justify-content": "flex-end", 
                           "margin-right": "50px",
                           "padding": "5px 15px",
                           }   
                ),
            ),
                    
        ], className="d-flex justify-content-between align-items-center w-100"),  # Space between
    ], className="bookmark-navigation bookmark-bar"
    )

def load_menu_config():
    """Load menu configuration from YAML file"""
    config_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "menu_structure.yaml"
    )
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


def generate_nav_links(items, parent_label=None):
    nav_links = []

    for label, content in items.items():
        if isinstance(content, dict):
            # If this level has a route, treat as a link
            if "route" in content:
                link_label = f"{parent_label} / {label}" if parent_label else label
                nav_links.append(
                    dbc.NavItem(
                        dbc.NavLink(link_label, 
                                    href=content["route"]
                                    ))
                )
            else:
                # Nested items: flatten into dropdown menu
                dropdown_items = []
                for sub_label, sub_content in content.items():
                    if isinstance(sub_content, dict) and "route" in sub_content:
                        dropdown_items.append(
                            dbc.DropdownMenuItem(sub_label, 
                                                 href=sub_content["route"],
                                                 style={"color": "#6c757d"})
                        )
                    elif isinstance(sub_content, dict):
                        # Third-level nesting
                        for subsub_label, subsub_content in sub_content.items():
                            if (
                                isinstance(subsub_content, dict)
                                and "route" in subsub_content
                            ):
                                combined_label = f"{sub_label} / {subsub_label}"
                                dropdown_items.append(
                                    dbc.DropdownMenuItem(
                                        combined_label, 
                                        href=subsub_content["route"],
                                        style={"color": "#6c757d"}
                                    )
                                )

                if dropdown_items:
                    nav_links.append(
                        dbc.DropdownMenu(
                            label=label,
                            nav=True,
                            in_navbar=True,
                            children=dropdown_items,
                            toggle_style={
                                "color": "#6c757d !important",
                                "font-size": "0.9rem",
                                "border": "none",
                                "background": "transparent"
                            }
                        )
                    )
    return nav_links
