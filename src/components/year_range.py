from dash import html, dcc
from typing import List, Dict, Optional

def create_year_range_component(
    base_id: str,
    years: List[int],
    default_from: Optional[int] = None,
    default_to: Optional[int] = None
) -> html.Div:
    """
    Create a year range component with two dropdowns for selecting from and to years.
    
    Args:
        base_id (str): Base ID for the component
        years (List[int]): List of available years
        default_from (int, optional): Default value for from year
        default_to (int, optional): Default value for to year
    
    Returns:
        html.Div: A div containing two dropdowns for year range selection
    """
    min_year, max_year = min(years), max(years)
    default_from = default_from or min_year
    default_to = default_to or max_year
    
    return html.Div([
        # Filter icon and label in one row
        html.Div([
            html.I(className="fas fa-calendar", 
                  style={'marginRight': '8px', 'color': '#666'}),
            html.Label(
                "Select Date Range",
                style={
                    'fontFamily': 'Inter',
                    'fontWeight': '500',
                    'color': '#333',
                    'fontSize': '14px'
                }
            ),
        ], style={
            'display': 'flex',
            'alignItems': 'center',
            'marginBottom': '8px'
        }),
        
        # Dropdowns in one row
        html.Div([
            # From Year dropdown
            html.Div([
                dcc.Dropdown(
                    id={
                        "type": "filter-dropdown",
                        "base_id": base_id,
                        "filter_id": "from_year"
                    },
                    options=[{'label': str(year), 'value': year} for year in sorted(years, reverse=True)],
                    value=default_from,
                    style={
                        'fontFamily': 'Inter',
                        'fontSize': '13px'
                    },
                    clearable=False,
                    placeholder="From"
                ),
            ], style={'width': '45%'}),
            
            # Separator
            html.Div("→", style={
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'width': '10%',
                'color': '#666'
            }),
            
            # To Year dropdown
            html.Div([
                dcc.Dropdown(
                    id={
                        "type": "filter-dropdown",
                        "base_id": base_id,
                        "filter_id": "to_year"
                    },
                    options=[{'label': str(year), 'value': year} for year in sorted(years, reverse=True)],
                    value=default_to,
                    style={
                        'fontFamily': 'Inter',
                        'fontSize': '13px'
                    },
                    clearable=False,
                    placeholder="To"
                ),
            ], style={'width': '45%'})
        ], style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'center',
            'width': '100%'
        })
    ], style={
        "padding": "12px",
        "backgroundColor": "white",
        "borderRadius": "4px",
        "boxShadow": "0 1px 3px rgba(0,0,0,0.1)",
        "marginBottom": "20px",
        "width": "100%",
        "position": "relative",
        "zIndex": "auto"
    }) 