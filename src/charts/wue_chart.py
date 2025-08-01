import plotly.express as px
import pandas as pd

def create_wue_scatter_plot(filtered_df, full_df=None, filters_applied=False):
    """
    Create WUE scatter plot
    
    Args:
        filtered_df: DataFrame to display
        filters_applied: Boolean indicating if filters are actively applied
        full_df: unfiltered DataFrame
    """

    if filtered_df.empty:
        return {
            'data': [],
            'layout': {
                'xaxis': {'title': 'Time Period', 'visible': True},
                'yaxis': {'title': 'Water Usage Effectiveness (WUE)', 'visible': True},
                'showlegend': False,
                'annotations': [{
                    'text': 'No data available for selected filters',
                    'xref': 'paper',
                    'yref': 'paper',
                    'x': 0.5,
                    'y': 0.5,
                    'showarrow': False,
                    'font': {'size': 16, 'color': 'gray'}
                }],
                'plot_bgcolor': 'white'
            }
        }
          
    # Create fields for hover text
    filtered_df = filtered_df.copy()
    filtered_df['region_text'] = filtered_df['region'].apply(lambda x: f'Region: {x}<br>' if pd.notna(x) and str(x).strip() else '')
    filtered_df['climate_text'] = filtered_df['assigned_climate_zones'].apply(lambda x: f'IECC Climate Zone: {x}<br>' if pd.notna(x) and str(x).strip() else '')
    filtered_df['measurement_text'] = filtered_df['measurement_category'].apply(lambda x: f'Measurement Category: {x}<br>' if pd.notna(x) and str(x).strip() else '')

    # Create the scatter plot
    wue_fig = px.scatter(
        filtered_df,
        x='time_period_value',
        y='metric_value',
        color='company_name' if filters_applied else None,
        labels={
            "time_period_value": "Time Period",
            "metric_value": "Water Usage Effectiveness (WUE)",
            "company_name": "Company Name"
        },
        custom_data=['company_name', 'region_text', 'climate_text', 'measurement_text']
    )

    if not filters_applied or filtered_df.empty:
        wue_fig.update_traces(
            marker=dict(color='lightgray', size=10, opacity=0.7),
            showlegend=False
        )
    else:
        wue_fig.update_traces(marker=dict(size=10))
        
        # Add background traces to foreground figure
        if full_df is not None and len(full_df) > len(filtered_df):
            # Get companies that are in the fildered data
            filtered_companies = set(filtered_df['company_name'].unique())
            
            # Filter background data to exclude companies already displayed
            background_df = full_df[~full_df['company_name'].isin(filtered_companies)].copy()
            
            if not background_df.empty:  # Only create background if there are companies to show
                background_df['region_text'] = background_df['region'].apply(lambda x: f'Region: {x}<br>' if pd.notna(x) and str(x).strip() else '')
                background_df['climate_text'] = background_df['assigned_climate_zones'].apply(lambda x: f'IECC Climate Zone: {x}<br>' if pd.notna(x) and str(x).strip() else '')
                background_df['measurement_text'] = background_df['measurement_category'].apply(lambda x: f'Measurement Category: {x}<br>' if pd.notna(x) and str(x).strip() else '')
                
                background_fig = px.scatter(
                    background_df, 
                    x='time_period_value', 
                    y='metric_value',
                    custom_data=['company_name', 'region_text', 'climate_text', 'measurement_text']
                )
                background_fig.update_traces(
                    marker=dict(color='lightgray', size=8, opacity=0.5),
                    showlegend=False
                )
                
                # Add to main figure
                for trace in background_fig.data:
                    wue_fig.add_trace(trace)
                
                # Reorder so background appears behind colored data
                wue_fig.data = wue_fig.data[-len(background_fig.data):] + wue_fig.data[:-len(background_fig.data)]
    
    wue_fig.update_layout(
        font_family="Inter",
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
        #range=[0, max(filtered_df['metric_value'].max() * 1.1, 2.2)],
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
        showlegend=filters_applied,
        template='simple_white'
    )

    # Update marker size and hover template
    wue_fig.update_traces(
        hovertemplate=(
            '<b>%{customdata[0]}</b><br>' +
            'Year: %{x}<br>' +
            'WUE: %{y:.2f}<br>' +
            '%{customdata[1]}' +  # Region (if exists)
            '%{customdata[2]}' +  # Climate zone (if exists)
            '%{customdata[3]}'    # Measurement level (if exists)
            '<extra></extra>'
        )
    )

    return wue_fig