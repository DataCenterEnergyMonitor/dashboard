from dash import html, dcc

def create_facility_scope_filter(df, chart_type):
    """Create facility scope dropdown filter"""
    scope_dropdown_id = f'{chart_type}-facility-scope-dropdown'
    return html.Div([
        html.Label(
            "Facility Scope:",
            style={'fontFamily': 'Roboto', 'fontWeight': '500'}
        ),
        dcc.Dropdown(
            id=scope_dropdown_id,
            options=[
                {"label": scope, "value": scope}
                for scope in df["facility_scope"].dropna().unique()
            ],
            value=df["facility_scope"].dropna().unique()[0],
            placeholder="Select a facility scope",
            style={'fontFamily': 'Roboto'}
        ),
    ], style={"marginBottom": "20px", "width": "100%"})

def create_company_filter(df, company_counts, chart_type):
    """Create company dropdown filter"""
    company_dropdown_id = f'{chart_type}-company-dropdown'
    return html.Div([
        html.Label(
            "Company:",
            style={'fontFamily': 'Roboto', 'fontWeight': '500'}
        ),
        dcc.Dropdown(
            id=company_dropdown_id,
            options=[
                {"label": "All", "value": "All"}
            ] + [
                {"label": company, "value": company}
                for company in df["company"].unique()
            ],
            multi=True,
            value=company_counts,
            placeholder="Select a company",
            style={'fontFamily': 'Roboto'}
        ),
    ], style={"marginBottom": "20px", "width": "100%"})

def create_geographical_scope_filter(df, chart_type):
    """Create geographical scope dropdown filter"""
    geographical_scope_dropdown_id = f'{chart_type}-geographical-scope-dropdown'
    return html.Div([
        html.Label(
            "Geographical Scope:",
            style={'fontFamily': 'Roboto', 'fontWeight': '500'}
        ),
        dcc.Dropdown(
            id=geographical_scope_dropdown_id,
            options=[
                {"label": "All", "value": "All"}
            ] + [
                {"label": geographical_scope, "value": geographical_scope}
                for geographical_scope in df["geographical_scope"].dropna().unique()
            ],
            multi=True,
            value="All",  # Changed from company_counts to "All"
            placeholder="Select a geographical scope",
            style={'fontFamily': 'Roboto'}
        ),
    ], style={"marginBottom": "20px", "width": "100%"})

def create_download_button(chart_type):
    """Create download button"""
    return html.Div([
        html.Button(
            "Download Data",
            id=f"{chart_type}-download-button",
            n_clicks=0,
            style={
                'backgroundColor': '#4CAF50',
                'color': 'white',
                'padding': '12px 24px',
                'border': 'none',
                'borderRadius': '4px',
                'cursor': 'pointer',
                'fontFamily': 'Roboto',
                'fontWeight': '500',
                'fontSize': '14px',
                'width': '200px'
            }
        ),
        dcc.Download(id=f"{chart_type}-download-dataframe"),
    ], style={"textAlign": "right", "marginBottom": "20px"})

def create_filters(df, company_counts, chart_type='pue', filter_config=None):
    """
    Create filter components for charts
    Args:
        df: DataFrame containing the data
        company_counts: List of most frequent companies
        chart_type: String indicating the chart type ('pue' or 'wue')
        filter_config: Dict specifying which filters to show {'facility_scope': True, 'company': True, etc.}
    Returns:
        html.Div containing the filter components
    """
    if filter_config is None:
        filter_config = {
            'facility_scope': True,
            'company': True,
            'geographical_scope': True
        }
    
    filters = []
    
    if filter_config.get('facility_scope'):
        filters.append(create_facility_scope_filter(df, chart_type))
    if filter_config.get('company'):
        filters.append(create_company_filter(df, company_counts, chart_type))
    if filter_config.get('geographical_scope'):
        filters.append(create_geographical_scope_filter(df, chart_type))
        
    filters.append(create_download_button(chart_type))
    
    return html.Div(filters)