import plotly.express as px
from .styles import get_pue_chart_layout
import pandas as pd

def create_pue_scatter_plot(filtered_df, selected_scope, industry_avg):
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

    pue_fig = px.scatter(
        filtered_df,
        x='applicable_year',
        y='real_pue',
        color='company',
        labels={
            "applicable_year": "Year",
            "real_pue": "Power Usage Effectiveness (PUE)",
            "company": "Company Name"
        },
        custom_data=['company', 'iea_region', 'iecc_climate_zone_s_','geographical_scope', 'pue_measurement_level']  # Set custom data for hover
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

    pue_fig.update_layout(
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
        range=[1, max(filtered_df['real_pue'].max() * 1.1, 1.8)],  # set y-axis to start at 1.0
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
    pue_fig.update_traces(
        marker=dict(size=10),
        selector=dict(mode='markers'),
        hovertemplate=(
            '<b>Company: %{customdata[0]}</b><br>'
            'Year: %{x}<br>'
            'PUE: %{y:.2f}<br>'
            'IEA Region: %{customdata[1]}<br>'
            'IECC Climate Zone: %{customdata[2]}<br>'
            'Location: %{customdata[3]}<br>'
            'Measurement Level: %{customdata[4]}<extra></extra>'
        )
    )

    # Add source citation with lower position
    pue_fig.add_annotation(
        text="Source: [TBD]",
        xref="paper",
        yref="paper",
        x=0,
        y=-0.25,
        showarrow=False,
        font=dict(size=10),
        align="left"
    )

    return pue_fig