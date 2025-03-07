def get_common_chart_layout():
    """
    Returns common layout settings for all charts in the application.
    This ensures visual consistency across the dashboard.
    """
    return {
        'font_family': "Roboto, sans-serif",
        'plot_bgcolor': 'white',
        'xaxis': dict(
            showgrid=False,
            showline=True,
            linecolor='black',
            linewidth=1,
            title_font=dict(size=14)
        ),
        'yaxis': dict(
            showgrid=False,
            showline=True,
            linecolor='black',
            linewidth=1,
            title_font=dict(size=14)
        ),
        'legend': dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        'margin': dict(t=100, b=100),
        'showlegend': True,
        'template': 'simple_white'
    }

def get_pue_chart_layout(filtered_df):
    """
    Returns specific layout settings for PUE charts, building upon common layout.
    """
    base_layout = get_common_chart_layout()
    
    # Add or override specific settings for PUE charts
    pue_specific = {
        'xaxis': {
            **base_layout['xaxis'],
            'dtick': 1  # Specific to PUE charts
        },
        'yaxis': {
            **base_layout['yaxis'],
            'range': [1, max(filtered_df['real_pue'].max() * 1.1, 1.8)]  # Specific to PUE charts
        }
    }
    
    return {**base_layout, **pue_specific}
