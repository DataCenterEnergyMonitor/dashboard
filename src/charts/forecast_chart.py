import plotly.express as px
from .styles import get_common_chart_layout
import pandas as pd

def create_forecast_scatter_plot(filtered_df, selected_scope, industry_avg):
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

    forecast_fig = px.scatter(
        filtered_df,
        x='prediction_year',
        y='annual_electricity_consumption_twh_',
        color='geographic_scope',
        labels={
            "prediction_year": "Year",
            "annual_electricity_consumption_twh_": "Annual Electricity Consumption Forecast (TWh)",
            "geographic_scope": "Location"
        },
        custom_data=['publisher_company',
                'annual_electricity_consumption_twh_',
                     'geographic_scope',
                     'author_type_s_',
                     'year',
                     'results_replicable_',
                     'peer_reviewed_',
                     'prediction_year']  # Set custom data for hover
    )
    # Add industry average line
    if industry_avg is not None:
        pue_fig.add_scatter(
            x=industry_avg['applicable_year'],
            y=industry_avg['real_pue'],
            mode='lines',
            name='Industry Average',
            line=dict(color='#bbbbbb', dash='dash', width=2)
        )
            
    forecast_fig.update_layout(
    font_family="Roboto",
    plot_bgcolor='white',
    xaxis=dict(
        showgrid=False,  # disable gridlines
        dtick=1,  # force yearly intervals
        showline=True,
        linecolor='black',
        linewidth=1,
        title_font=dict(size=14)
    ),
    yaxis=dict(
        showgrid=False,  # Disable gridlines
        range=[0, max(filtered_df['annual_electricity_consumption_twh_'].max() * 1.1, 1.8)],  # set y-axis to start at 1.0
        showline=True,
        linecolor='black',
        linewidth=1,
        title_font=dict(size=14)
    ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        margin=dict(t=100, b=100),  # set bottom margin for citation
        showlegend=True,
        template='simple_white'
    )

    # Update marker size and hover template
    forecast_fig.update_traces(
        marker=dict(size=10),
        selector=dict(mode='markers'),
        hovertemplate=(
            '<b>Publisher: %{customdata[0]}</b><br>'
            'Forecast: %{y:.2f}<br>'
            'Forecast Year: %{x}<br>'
            'Geography Scope: %{customdata[2]}<br>'
            'Author Type: %{customdata[3]}<br>'
            'Publication Year: %{customdata[4]}<extra></extra>'
        )
    )

    # Add source citation with lower position
    forecast_fig.add_annotation(
        text="Source: [TBD]",
        xref="paper",
        yref="paper",
        x=0,
        y=-0.25,
        showarrow=False,
        font=dict(size=10),
        align="left"
    )

    return forecast_fig