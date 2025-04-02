from dash import html, dcc


def create_filter_panel(filter_components, title="Filters"):
    """
    Creates a filter panel component.

    Args:
        filter_components: List of filter components to display
        title: Title of the filter panel
    """
    return html.Div(
        [
            # Filter icon header - left aligned
            html.Div(
                [
                    html.I(
                        className="fas fa-filter",
                        style={
                            "fontSize": "24px",
                            "color": "#4CAF50",  # '#3d8b40',
                            "marginBottom": "20px",
                        },
                    )
                ],
                style={
                    "display": "flex",
                    "justifyContent": "flex-start",  # Left aligned
                    "width": "100%",
                },
            ),
            # Filter components
            filter_components,
        ],
        id="filter-panel",
        style={
            "width": "260px",
            "backgroundColor": "white",
            "padding": "20px",
            "boxShadow": "none",  # Remove shadow
            "height": "calc(100vh - 76px)",  # Extend all the way to the bottom (56px navbar + 20px padding)
            "overflowY": "auto",
            "position": "relative",
        },
    )
