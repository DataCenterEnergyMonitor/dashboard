import plotly.express as px
from .styles import get_common_chart_layout

def create_wue_scatter_plot(filtered_df, selected_scope="Fleet-wide", industry_avg=None):
    if filtered_df.empty or selected_scope is None:
        # Return an empty figure with a message
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
    
    wue_fig = px.scatter(
        filtered_df,
        x='applicable_year',
        y='wue',
        color='company',
        labels={
            "applicable_year": "Year",
            "wue": "Water Usage Effectiveness (WUE)",
            "company": "Company Name"
        },
        custom_data=['company']
    )
    
    # Add industry average line
    if industry_avg is not None:
        wue_fig.add_scatter(
            x=industry_avg['applicable_year'],
            y=industry_avg['wue'],
            mode='lines',
            name='Industry Average',
            line=dict(color='#bbbbbb', dash='dash', width=2),
    )

    # Apply layout settings
    wue_fig.update_layout(get_common_chart_layout())

    # Update marker size
    wue_fig.update_traces(
        marker=dict(size=10), 
        selector=dict(mode='markers'),
        hovertemplate=(
            '<b>Company: %{customdata[0]}</b><br>'
            'Year: %{x}<br>'
            'WUE: %{y:.2f}<br>'
        ))
    
    # Add source citation
    wue_fig.add_annotation(
        text="Source: [TBD]",
        xref="paper",
        yref="paper",
        x=0,
        y=-0.25,
        showarrow=False,
        font=dict(size=10),
        align="left"
    )

    return wue_fig
