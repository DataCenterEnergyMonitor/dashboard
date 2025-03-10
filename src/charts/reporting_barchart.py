import plotly.express as px
from .styles import get_common_chart_layout
import pandas as pd

def create_reporting_bar_plot(filtered_df, selected_scope=None, industry_avg=None):
    """
    Create a bar plot showing the number of reporting companies by year.
    
    Args:
        filtered_df: DataFrame containing the reporting data
        selected_scope: Selected reporting scope from the dropdown
        industry_avg: Not used for this chart, kept for interface consistency
    """
    print("Filtered DataFrame shape:", filtered_df.shape)  # Debug print
    print("Selected scope:", selected_scope)  # Debug print
    
    if filtered_df.empty:
        return {
            'data': [],
            'layout': {
                'xaxis': {'visible': False},
                'yaxis': {'visible': False},
                'annotations': [{
                    'text': 'No data available for the selected filters',
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
    
    print("Grouped DataFrame:", grouped_df.head())  # Debug print

    reporting_fig = px.bar(
        grouped_df,
        x='reported_data_year',
        y='num_companies',
        color='reporting_scope',  # Add color by reporting scope
        labels={
            "reported_data_year": "Year",
            "num_companies": "Number of Companies Reporting",
            "reporting_scope": "Reporting Scope"
        },
        barmode='group'  # Group bars by year
    )

    # Get common layout and update specific properties
    layout = get_common_chart_layout()
    layout.update(
        xaxis=dict(
            title="Year",
            tickmode='linear',
            dtick=1  # Show all years
        ),
        yaxis=dict(
            title="Number of Companies Reporting",
            tickmode='linear'
        ),
        legend=dict(
            orientation="h",  # horizontal legend
            yanchor="bottom",
            y=1.02,  # Position above the chart
            xanchor="right",
            x=1
        )
    )
    
    reporting_fig.update_layout(layout)

    # Update hover template
    reporting_fig.update_traces(
        hovertemplate=(
            'Year: %{x}<br>'
            'Number of Companies: %{y}<br>'
            'Reporting Scope: %{customdata[0]}<br>'
        ),
        customdata=grouped_df[['reporting_scope']]
    )

    return reporting_fig