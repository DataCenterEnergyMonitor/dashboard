import dash_bootstrap_components as dbc
from dash import html, dcc
import yaml
import os


def create_bookmark_tabs(
    tabs_config,
    active_tab_id="tab-1",
    data_page_parent=None,
    id_prefix="",
):
    """
    Create bookmark-styled tab navigation bar.

    This is a generic, reusable component that can be used across different pages.
    Use the `id_prefix` parameter to namespace IDs and avoid conflicts.

    Args:
        tabs_config: List of dicts with 'label' and 'value' keys
            e.g., [{"label": "Tab 1", "value": "tab-1"}, {"label": "Tab 2", "value": "tab-2"}]
        active_tab_id: ID of the initially active tab (e.g., "tab-1")
        data_page_parent: Optional parent key for navbar links from menu_structure.yaml
        id_prefix: Prefix for all component IDs to avoid conflicts between pages.
            e.g., "rt-" creates IDs like "rt-active-tab-store", "rt-tab-btn-tab-1"
            Leave empty for backward compatibility with existing pages.

    Returns:
        html.Div containing the bookmark-styled tabs and hidden store

    Example usage:
        # For global_policies page (no prefix - backward compatible)
        create_bookmark_tabs(
            tabs_config=[{"label": "Tab 1", "value": "tab-1"}],
            active_tab_id="tab-1",
        )

        # For company_reporting_trends page (with prefix)
        create_bookmark_tabs(
            tabs_config=[{"label": "Reporting", "value": "tab-1"}],
            active_tab_id="tab-1",
            id_prefix="rt-",
        )
    """

    # Define styles for active and inactive tabs
    active_style = {
        "border-radius": "15px",
        "border": "none",
        "backgroundColor": "rgba(0, 88, 141, 0.9)",
        "font-size": "0.85rem",
        "padding": "5px 20px",
        "text-decoration": "none",
        "color": "#ffffff",
        "display": "inline-block",
    }

    inactive_style = {
        "border-radius": "15px",
        "border": "none",
        "backgroundColor": "transparent",
        "font-size": "0.85rem",
        "padding": "5px 15px",
        "text-decoration": "none",
        "color": "#6c757d",
        "display": "inline-block",
    }

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
    tab_buttons = []
    for tab in tabs_config:
        is_active = tab["value"] == active_tab_id
        # Button ID: {prefix}tab-btn-{value}
        button_id = f"{id_prefix}tab-btn-{tab['value']}"
        button = dbc.Button(
            tab["label"],
            id=button_id,
            n_clicks=1 if is_active else 0,
            color="link",  # Use link to avoid Bootstrap button styling
            size="sm",
            className="me-2 mb-2 bookmark-tab-btn",
            style=active_style if is_active else inactive_style,
        )
        tab_buttons.append(button)

    # Store ID: {prefix}active-tab-store
    store_id = f"{id_prefix}active-tab-store"
    tab_store = dcc.Store(id=store_id, data=active_tab_id)

    # Collapse ID: {prefix}bookmark-tabs-navbar-collapse
    collapse_id = f"{id_prefix}bookmark-tabs-navbar-collapse"

    return html.Div(
        [
            tab_store,  # Hidden store for tab state
            html.Div(
                [
                    # Left side - tab buttons
                    html.Div(
                        tab_buttons,
                        className="d-flex",
                        style={
                            "justify-content": "flex-start",
                            "flex-wrap": "nowrap",
                            "overflow": "visible",
                        },
                    ),
                    # Right-aligned collapse menu (if nav_links exist)
                    html.Div(
                        dbc.Collapse(
                            id=collapse_id,
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
                className="d-flex justify-content-between align-items-center w-100",
            ),
        ],
        className="bookmark-navigation bookmark-bar",
        style={
            "overflow": "visible",
            "whiteSpace": "nowrap",
        },
    )


def get_tab_styles():
    """
    Return the active and inactive tab styles for use in callbacks.

    Returns:
        tuple: (active_style, inactive_style)

    Example usage in callback:
        from components.bookmark_tabs import get_tab_styles

        active_style, inactive_style = get_tab_styles()
        style1 = active_style if active_tab == "tab-1" else inactive_style
    """
    active_style = {
        "border-radius": "15px",
        "border": "none",
        "backgroundColor": "rgba(0, 88, 141, 0.9)",
        "font-size": "0.85rem",
        "padding": "5px 20px",
        "text-decoration": "none",
        "color": "#ffffff",
        "display": "inline-block",
    }

    inactive_style = {
        "border-radius": "15px",
        "border": "none",
        "backgroundColor": "transparent",
        "font-size": "0.85rem",
        "padding": "5px 15px",
        "text-decoration": "none",
        "color": "#6c757d",
        "display": "inline-block",
    }

    return active_style, inactive_style


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
