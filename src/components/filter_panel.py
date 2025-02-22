from dash import html
import dash_bootstrap_components as dbc

def create_filter_panel(filter_components, title="Filters"):
    """
    Creates an expandable filter panel component.
    
    Args:
        filter_components: List of filter components to display
        title: Title of the filter panel
    """
    return html.Div([
        dbc.Accordion([
            dbc.AccordionItem(
                filter_components,
                title=title,
                item_id="filter-panel",
            )
        ], start_collapsed=False, flush=True)
    ], style={
        'width': '300px',  # Fixed width for the filter panel
        'minWidth': '300px',
        'padding': '20px',
        'borderRight': '1px solid #ddd',
        'height': '100vh',
        'overflowY': 'auto'
    }) 