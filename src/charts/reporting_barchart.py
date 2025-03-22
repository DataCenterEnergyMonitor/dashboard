import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from .styles import get_bar_chart_layout

# Define color palette for reporting scopes
REPORTING_SCOPE_COLORS = {
    'Company Wide Electricity Use': 'rgba(23, 79, 138, 0.8)',
    'Data Center Electricity Use': '#C16597',  
    'Data Center Fuel Use': '#AACE63', 
    'Data Center Water Use': '#23CDC6'  
}

def create_reporting_bar_plot(df: pd.DataFrame) -> go.Figure:
    """
    Create a stacked bar plot showing the number of reporting companies by year and scope.
    
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

    # Group the data by year and scope, count unique companies
    grouped_df = (df
                 .groupby(['reported_data_year', 'reporting_scope'])
                 .agg({'company_name': 'nunique'})
                 .reset_index()
                 .rename(columns={'company_name': 'num_companies'}))
    
    # Create the stacked bar chart
    fig = px.bar(
        grouped_df,
        x='reported_data_year',
        y='num_companies',
        color='reporting_scope',
        color_discrete_map=REPORTING_SCOPE_COLORS,
        barmode='stack'
    )

    # Update layout using common style
    fig.update_layout(get_bar_chart_layout())

    # Update hover template
    fig.update_traces(
        hovertemplate='%{y} Companies<extra></extra>'
    )

    return fig