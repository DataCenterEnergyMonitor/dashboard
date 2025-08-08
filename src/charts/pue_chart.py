import plotly.express as px
import pandas as pd

def create_pue_scatter_plot(filtered_df, full_df=None, filters_applied=False):
    """
    Create PUE scatter plot
    
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
                'yaxis': {'title': 'Power Usage Effectiveness (PUE)', 'visible': True},
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
    def create_hover_text(df):
        """Process DataFrame fields for hover text display"""
        df['metric_type'] = df['metric_type'].apply(
            lambda x: f'PUE Type: {x}<br>' if pd.notna(x) and str(x).strip() else '')
        df['measurement_category'] = df['measurement_category'].apply(
            lambda x: f'Measurement Category: {x}<br>' if pd.notna(x) and str(x).strip() else '')
        df['time_period_category'] = df['time_period_category'].apply(
            lambda x: f'Time Period Category: {x}<br>' if pd.notna(x) and str(x).strip() else '')
        df['facility_scope'] = df['facility_scope'].apply(
            lambda x: f'Facility Scope: {x}<br>' if pd.notna(x) and str(x).strip() else '')
        df['region_text'] = df['region'].apply(
            lambda x: f'Region: {x}<br>' if pd.notna(x) and str(x).strip() else '')
        df['country'] = df['country'].apply(
            lambda x: f'Country: {x}<br>' if pd.notna(x) and str(x).strip() else '')
        df['city'] = df['city'].apply(
            lambda x: f'City: {x}<br>' if pd.notna(x) and str(x).strip() else '')
        df['climate_text'] = df['assigned_climate_zones'].apply(
            lambda x: f'IECC Climate Zone: {x}<br>' if pd.notna(x) and str(x).strip() else '')

    custom_data = [
        'company_name', 
        'metric_type',
        'measurement_category',
        'time_period_category',
        'facility_scope',
        'region_text',
        'country',
        'city',
        'climate_text'
    ]
    
    filtered_df = filtered_df.copy()
    create_hover_text(filtered_df)
    # Create the scatter plot
    pue_fig = px.scatter(
            filtered_df,
            x='time_period_value',
            y='metric_value',
            color='company_name' if filters_applied else None,
            labels={
                "time_period_value": "Time Period",
                "metric_value": "Power Usage Effectiveness (PUE)",
                "company_name": "Company Name"
            },
            custom_data=custom_data
        )

    if not filters_applied:
        pue_fig.update_traces(
            marker=dict(color='lightgray', size=10, opacity=0.7),
            showlegend=False
        )
    else:
        pue_fig.update_traces(marker=dict(size=10))
        
        # Add background traces to foreground figure
        if full_df is not None and len(full_df) > len(filtered_df):
            # Get companies that are in the fildered data
            filtered_companies = set(filtered_df['company_name'].unique())
            
            # Filter background data to exclude companies already displayed
            background_df = full_df[~full_df['company_name'].isin(filtered_companies)].copy()
            
            if not background_df.empty:  # Only create background if there are companies to show
                create_hover_text(background_df)

                background_fig = px.scatter(
                    background_df, 
                    x='time_period_value', 
                    y='metric_value',
                    custom_data=custom_data
                )
                background_fig.update_traces(
                    marker=dict(color='lightgray', size=8, opacity=0.5),
                    showlegend=False
                )
                
                # Add to main figure
                for trace in background_fig.data:
                    pue_fig.add_trace(trace)
                
                # Reorder so background appears behind colored data
                pue_fig.data = pue_fig.data[-len(background_fig.data):] + pue_fig.data[:-len(background_fig.data)]
    
    pue_fig.update_layout(
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
        range=[1, max(filtered_df['metric_value'].max() * 1.1, 2.2)],  # set y-axis to start at 1.0
        showline=True,
        linecolor='black',
        linewidth=1,
        title_font=dict(size=14)
    ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.01,
            xanchor='right',
            x=1
        ),
        #margin=dict(t=100, b=100),  # set bottom margin for citation
        showlegend=filters_applied,
        template='simple_white'
    )

    # Update marker size and hover template
    pue_fig.update_traces(
        hovertemplate=(
            '<b>%{customdata[0]}</b><br>' + # company name
            'PUE: %{y:.2f}<br>' + # PUE value
            '%{customdata[1]}' + # metric type (Measured or Design)
            '%{customdata[2]}' + # measurement level (if exists)
            '%{customdata[3]}' + # time period category
            'Time Period: %{x}<br>' + # Time period value
            '%{customdata[4]}' + # facility scope
            '%{customdata[5]}' +  # Region (if exists)
            '%{customdata[6]}' +  # country (if exists)
            '%{customdata[7]}' +  # city (if exists)
            '%{customdata[8]}' +  # Climate zone (if exists)
            '<extra></extra>'
        )
    )
    return pue_fig