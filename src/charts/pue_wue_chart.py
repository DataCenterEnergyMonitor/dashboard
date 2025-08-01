import plotly.express as px
import pandas as pd

def create_pue_wue_scatter_plot(filtered_df, full_df=None, filters_applied=False):
    """
    Create WUE vs PUE scatter plot
    
    Args:
        filtered_df: DataFrame to display
        filters_applied: Boolean indicating if filters are actively applied
        full_df: unfiltered DataFrame
    """
    print(f"=== PUE/WUE CHART DEBUG ===")
    print(f"filtered_df shape: {filtered_df.shape}")
    print(f"filters_applied: {filters_applied}")
    if not filtered_df.empty:
        print(f"Columns: {list(filtered_df.columns)}")
        print(f"Sample data:")
        print(filtered_df[['company_name', 'metric_value', 'wue_value']].head())
        print(f"Unique companies: {filtered_df['company_name'].unique()}")
        print(f"Company name nulls: {filtered_df['company_name'].isnull().sum()}")
        print(f"metric_value nulls: {filtered_df['metric_value'].isnull().sum()}")
        print(f"wue_value nulls: {filtered_df['wue_value'].isnull().sum()}")
        print(f"Company name dtype: {filtered_df['company_name'].dtype}")
        
        # Check for actual values vs empty strings
        print(f"Company name empty strings: {(filtered_df['company_name'] == '').sum()}")
        print(f"Company name sample values: {filtered_df['company_name'].head().tolist()}")
    else:
        print("❌ filtered_df is empty!")

    if filtered_df.empty:
        return {
            'data': [],
            'layout': {
                'xaxis': {'title': 'Power Usage Effectiveness (PUE)', 'visible': True},
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
    pue_wue_fig = px.scatter(
        filtered_df,
        x='metric_value',
        y='wue_value',
        color='company_name' if filters_applied else None,
        labels={
            "metric_value": "Power Usage Effectiveness (PUE)",
            "wue_value": "Water Usage Effectiveness (WUE)",
            "company_name": "Company Name"
        },
        custom_data=['company_name', 'region_text', 'climate_text', 'measurement_text']
    )

    if not filters_applied:
        pue_wue_fig.update_traces(
            marker=dict(color='lightgray', size=10, opacity=0.7),
            showlegend=False
        )
    else:
        pue_wue_fig.update_traces(marker=dict(size=10))
        
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
                    x='metric_value', 
                    y='wue_value',
                    custom_data=['company_name', 'region_text', 'climate_text', 'measurement_text']
                )
                background_fig.update_traces(
                    marker=dict(color='lightgray', size=8, opacity=0.5),
                    showlegend=False
                )
                
                # Add to main figure
                for trace in background_fig.data:
                    pue_wue_fig.add_trace(trace)
                
                # Reorder so background appears behind colored data
                pue_wue_fig.data = pue_wue_fig.data[-len(background_fig.data):] + pue_wue_fig.data[:-len(background_fig.data)]
    
    pue_wue_fig.update_layout(
        font_family="Inter",
        plot_bgcolor='white',
        xaxis=dict(
            showgrid=False,  # disable gridlines
            dtick=0.2,  # force yearly intervals
            range=[0.8, 2.4],  # set y-axis to start at 1.0,
            showline=True,
            linecolor='black',
            linewidth=1,
            title_font=dict(size=14)
        ),

        yaxis=dict(
            showgrid=False,  # Disable gridlines
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
    pue_wue_fig.update_traces(
        hovertemplate=(
            '<b>%{customdata[0]}</b><br>' +
            'PUE: %{x:.2f}<br>' +
            'WUE: %{y:.2f}<br>' +
            '%{customdata[1]}' +  # Region (if exists)
            '%{customdata[2]}' +  # Climate zone (if exists)
            '%{customdata[3]}'    # Measurement level (if exists)
            '<extra></extra>'
        )
    )

    return pue_wue_fig