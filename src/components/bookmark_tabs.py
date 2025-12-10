import dash_bootstrap_components as dbc
from dash import html, dcc
import yaml
import os


def create_bookmark_tabs(tabs_config, active_tab_id="tab-1", data_page_parent=None):
    """
    Create bookmark-styled tab navigation bar

    Args:
        tabs_config: List of dicts with 'label' and 'value' keys
        active_tab_id: ID of the initially active tab
        data_page_parent: Optional parent for navbar links

    Returns:
        html.Div containing the bookmark-styled tabs and hidden store
    """

    # Load menu structure if data_page_parent is provided
    nav_links = []
    if data_page_parent:
        menu_structure = load_menu_config()
        navbar_items = (
            menu_structure.get("navbar", {})
            .get("data_page", {})
            .get(data_page_parent, {})
        )
        nav_links = generate_nav_links(navbar_items)

    # Create tab buttons styled like bookmark buttons
    # Note: Initial styles are set via callback, not here, to avoid Dash conflicts
    tab_buttons = []
    for tab in tabs_config:
        is_active = tab["value"] == active_tab_id
        button = dbc.Button(
            tab["label"],
            id=f"tab-btn-{tab['value']}",
            n_clicks=1 if is_active else 0,
            color="outline-primary",  # Default color, will be overridden by callback
            size="sm",
            className="me-2 mb-2 bookmark-tab-btn",
            # Don't set style here - let the callback handle it to avoid conflicts
        )
        tab_buttons.append(button)

    # Hidden store to track active tab
    tab_store = dcc.Store(id="active-tab-store", data=active_tab_id)

    return html.Div(
        [
            tab_store,  # Hidden store for tab state
            html.Div(
                [
                    # Left side - tab buttons
                    html.Div(
                        tab_buttons,
                        className="d-flex flex-wrap",
                        style={"justify-content": "flex-start"},
                    ),
                    # Right-aligned collapse menu (if nav_links exist)
                    html.Div(
                        dbc.Collapse(
                            id="navbar-collapse",
                            is_open=True,
                            navbar=True,
                            className="justify-content-end",
                            children=[
                                dbc.Nav(nav_links, navbar=True, className="ms-auto"),
                            ]
                            if nav_links
                            else [],
                            style={
                                "justify-content": "flex-end",
                                "margin-right": "100px",
                                "padding": "5px 15px",
                            },
                        ),
                    )
                    if nav_links
                    else html.Div(),
                ],
                className="d-flex justify-content-between align-items-center w-200",
            ),
        ],
        className="bookmark-navigation bookmark-bar",
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
                    dbc.NavItem(dbc.NavLink(link_label, href=content["route"]))
                )
            else:
                # Nested items: flatten into dropdown menu
                dropdown_items = []
                for sub_label, sub_content in content.items():
                    if isinstance(sub_content, dict) and "route" in sub_content:
                        dropdown_items.append(
                            dbc.DropdownMenuItem(
                                sub_label,
                                href=sub_content["route"],
                                style={"color": "#6c757d"},
                            )
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
                                        style={"color": "#6c757d"},
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
                                "background": "transparent",
                            },
                        )
                    )
    return nav_links
