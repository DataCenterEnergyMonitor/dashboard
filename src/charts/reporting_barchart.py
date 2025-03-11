import plotly.express as px
from .styles import get_bar_chart_layout

# Define color palette for reporting scopes
REPORTING_SCOPE_COLORS = {
    'Company Wide Electricity Use': '#174F8A', # Blue
    'Data Center Electricity Use': '#C16597',   # Green
    'Data Center Fuel Use': '#AACE63', #C7C562',  # Orange
    'Data Center Water Use': '#23CDC6'   # Purple
}

def create_reporting_bar_plot(filtered_df):
    """
    Create a stacked bar plot showing the number of reporting companies by year and scope.
    """
    if filtered_df.empty:
        return {
            'data': [],
            'layout': {
                'xaxis': {'visible': False},
                'yaxis': {'visible': False},
                'annotations': [{
                    'text': 'No data available',
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 20}
                }]
            }
        }

    # Group the data by year and scope, count unique companies
    grouped_df = (filtered_df
                 .groupby(['reported_data_year', 'reporting_scope'])
                 .agg({'company_name': 'nunique'})
                 .reset_index()
                 .rename(columns={'company_name': 'num_companies'}))
    
    # Create the stacked bar chart
    reporting_fig = px.bar(
        grouped_df,
        x='reported_data_year',
        y='num_companies',
        color='reporting_scope',
        color_discrete_map=REPORTING_SCOPE_COLORS,
        barmode='stack'
    )

    # Update layout using common style
    reporting_fig.update_layout(get_bar_chart_layout())

    # Update hover template
    reporting_fig.update_traces(
        hovertemplate='%{y} Companies<extra></extra>'
    )

    return reporting_fig