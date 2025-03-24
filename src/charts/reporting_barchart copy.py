import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from .styles import get_bar_chart_layout

# Define color palette for reporting scopes
REPORTING_SCOPE_COLORS = {
    'Company Wide Electricity Use': 'rgba(23, 79, 138, 0.8)',
    'Data Center Electricity Use': '#C16597',
    'Data Center Fuel Use': '#AACE63',
    #'Data Center Water Use': '#23CDC6'
}

def create_reporting_bar_plot(df: pd.DataFrame) -> go.Figure:
    """
    Create a stacked bar plot showing the number of reporting companies by year, scope, and status.
    
    Args:
        df (pd.DataFrame): Filtered dataframe containing reporting data
        
    Returns:
        go.Figure: Plotly figure object with stacked bars showing reporting trends
    """
    if df.empty:
        return go.Figure().update_layout(
            xaxis={'visible': False},
            yaxis={'visible': False},
            annotations=[{
                'text': 'No data available',
                'xref': 'paper',
                'yref': 'paper',
                'showarrow': False,
                'font': {'size': 20}
            }]
        )
    
    # Group the data by year, scope, and status, count unique companies
    grouped_df = (df
        .groupby(['reported_data_year', 'reporting_scope', 'reporting_status'])
        .agg({'company_name': 'nunique'})
        .reset_index()
        .rename(columns={'company_name': 'num_companies'}))
    
    # Create an empty figure
    fig = go.Figure()
    
    # Add bars for each combination of scope and status
    for scope in REPORTING_SCOPE_COLORS:
        # Skip if this scope isn't in the data
        if scope not in grouped_df['reporting_scope'].unique():
            continue
            
        # Add reported data (solid color)
        scope_reported = grouped_df[(grouped_df['reporting_scope'] == scope) & 
                                    (grouped_df['reporting_status'] == 'Reported')]
        if not scope_reported.empty:
            fig.add_trace(go.Bar(
                x=scope_reported['reported_data_year'],
                y=scope_reported['num_companies'],
                name=scope,
                legendgroup=scope,
                legendgrouptitle_text=scope,
                marker_color=REPORTING_SCOPE_COLORS[scope],
                customdata=[f"Reported: {count}" 
                           for count in scope_reported['num_companies']],
                hovertemplate='%{customdata}<extra></extra>'
            ))
        
        # Add pending data (striped/patterned version)
        scope_pending = grouped_df[(grouped_df['reporting_scope'] == scope) & 
                                   (grouped_df['reporting_status'] == 'Pending data submission')]
        if not scope_pending.empty:
            base_color = REPORTING_SCOPE_COLORS[scope]
            # Create a lighter version for pending
            if base_color.startswith('#'):
                r = int(base_color[1:3], 16)
                g = int(base_color[3:5], 16)
                b = int(base_color[5:7], 16)
                lighter_color = f"rgba({r}, {g}, {b}, 0.5)"
            elif base_color.startswith('rgba'):
                rgba_parts = base_color.replace('rgba(', '').replace(')', '').split(',')
                r, g, b = rgba_parts[0].strip(), rgba_parts[1].strip(), rgba_parts[2].strip()
                lighter_color = f"rgba({r}, {g}, {b}, 0.5)"
            else:
                lighter_color = base_color
                
            fig.add_trace(go.Bar(
                x=scope_pending['reported_data_year'],
                y=scope_pending['num_companies'],
                name='Pending data submission',
                legendgroup=scope,
                legendgrouptitle_text=scope,
                marker_color=lighter_color,
                #marker_pattern_type='\\',
                customdata=[f"Pending data submission: {count}" 
                           for count in scope_pending['num_companies']],
                hovertemplate='%{customdata}<extra></extra>'
            ))
    
    # Set to stacked mode
    fig.update_layout(barmode='stack')
    
    # Update layout using common style
    fig.update_layout(get_bar_chart_layout())
    
    # Improve legend layout with grouping
    fig.update_layout(
        legend=dict(
            groupclick="togglegroup",  # clicking on group name toggles all items
            tracegroupgap=5            # gap between groups in pixels
        ),
        xaxis_title="Year",
        yaxis_title="Number of Companies Reporting"
    )
    
    return fig