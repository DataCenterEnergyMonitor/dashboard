import plotly.express as px
from .styles import get_common_chart_layout
import pandas as pd

def create_forecast_scatter_plot(filtered_df):
    """Create a scatter plot for energy forecast data"""
    print("Forecast data columns:", filtered_df.columns.tolist())
    print("Forecast data shape:", filtered_df.shape)
    print("Sample data types:", filtered_df.dtypes[['prediction_year', 'annual_electricity_consumption_twh_']])
    print("Sample values:", filtered_df[['prediction_year', 'annual_electricity_consumption_twh_']].head())
    
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

    try:
        # Convert and clean the data
        filtered_df['prediction_year'] = pd.to_numeric(filtered_df['prediction_year'].astype(str).str.strip(), errors='coerce')
        filtered_df['annual_electricity_consumption_twh_'] = pd.to_numeric(filtered_df['annual_electricity_consumption_twh_'].astype(str).str.strip(), errors='coerce')
        
        # Remove rows where either value is NaN
        filtered_df = filtered_df.dropna(subset=['prediction_year', 'annual_electricity_consumption_twh_'])
        
        print("After numeric conversion and NaN removal:")
        print("Data shape:", filtered_df.shape)
        print("Sample values after conversion:", filtered_df[['prediction_year', 'annual_electricity_consumption_twh_']].head())
        print("Unique years:", sorted(filtered_df['prediction_year'].unique()))
        print("Value ranges:", {
            'year_min': filtered_df['prediction_year'].min(),
            'year_max': filtered_df['prediction_year'].max(),
            'twh_min': filtered_df['annual_electricity_consumption_twh_'].min(),
            'twh_max': filtered_df['annual_electricity_consumption_twh_'].max()
        })

        # Create scatter plot
        forecast_fig = px.scatter(
            filtered_df,
            x='prediction_year',
            y='annual_electricity_consumption_twh_',
            color='geographic_scope',
            labels={
                "prediction_year": "Forecast Year",
                "annual_electricity_consumption_twh_": "Annual Electricity Consumption (TWh)",
                "geographic_scope": "Location"
            },
            custom_data=['publisher_company',
                        'annual_electricity_consumption_twh_',
                        'geographic_scope',
                        'author_type_s_',
                        'year',
                        'peer_reviewed_'],
            template='simple_white'
        )

        # Update layout
        forecast_fig.update_layout(
            font_family="Inter",
            plot_bgcolor='white',
            xaxis=dict(
                showgrid=True,
                showline=True,
                linecolor='black',
                linewidth=1,
                title_font=dict(size=14),
                type='linear'
            ),
            yaxis=dict(
                showgrid=True,
                showline=True,
                linecolor='black',
                linewidth=1,
                title_font=dict(size=14),
                type='linear'
            ),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            ),
            margin=dict(t=100, b=100),
            showlegend=True,
            template='simple_white'
        )

        # Update hover template
        forecast_fig.update_traces(
            marker=dict(size=10),
            hovertemplate=(
                '<b>Publisher: %{customdata[0]}</b><br>'
                'Forecast: %{y:.2f} TWh<br>'
                'Forecast Year: %{x}<br>'
                'Location: %{customdata[2]}<br>'
                'Author Type: %{customdata[3]}<br>'
                'Publication Year: %{customdata[4]}<br>'
                'Peer Reviewed: %{customdata[5]}<extra></extra>'
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
    
    except Exception as e:
        print(f"Error creating forecast chart: {e}")
        print("Data sample causing error:", filtered_df.head())
        raise e