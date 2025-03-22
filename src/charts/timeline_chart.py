import plotly.graph_objects as go

# Define color palette for reporting scopes
REPORTING_SCOPE_COLORS = {
    'No Reporting': '#e0e0e0',
    'Company Wide Electricity Use': 'rgba(23, 79, 138, 0.8)',
    'Data Center Electricity Use': '#C16597',
    'Both': '#4CAF50'
}

def create_timeline_bar_plot(filtered_df):
    """Create a heatmap showing companies' reporting patterns over time."""
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

    # Get unique companies and years
    companies = sorted(filtered_df['company_name'].unique())
    years = sorted(filtered_df['reported_data_year'].unique())
    
    # Create matrix for heatmap
    z_data = []
    hover_texts = []
    
    for company in companies:
        row_data = []
        row_hover = []
        
        for year in years:
            year_data = filtered_df[
                (filtered_df['company_name'] == company) & 
                (filtered_df['reported_data_year'] == year)
            ]
            
            scopes = set(year_data['reporting_scope'].unique())
            company_wide = 'Company Wide Electricity Use' in scopes
            data_center = 'Data Center Electricity Use' in scopes
            
            if company_wide and data_center:
                value = 3
                text = f"{company} ({year})<br>Reporting: Both electricity usages"
            elif company_wide:
                value = 1
                text = f"{company} ({year})<br>Reporting: Company Wide Electricity Use"
            elif data_center:
                value = 2
                text = f"{company} ({year})<br>Reporting: Data Center Electricity Use"
            else:
                value = 0
                text = f"{company} ({year})<br>No electricity reporting"
            
            row_data.append(value)
            row_hover.append(text)
            
        z_data.append(row_data)
        hover_texts.append(row_hover)

    # Create the heatmap trace
    heatmap = go.Heatmap(
        z=z_data,
        x=years,  # Use integer years
        y=companies,
        text=hover_texts,
        hoverongaps=False,
        hoverinfo='text',
        colorscale=[
            [0.0, REPORTING_SCOPE_COLORS['No Reporting']],
            [0.25, REPORTING_SCOPE_COLORS['No Reporting']],
            [0.25, REPORTING_SCOPE_COLORS['Company Wide Electricity Use']],
            [0.5, REPORTING_SCOPE_COLORS['Company Wide Electricity Use']],
            [0.5, REPORTING_SCOPE_COLORS['Data Center Electricity Use']],
            [0.75, REPORTING_SCOPE_COLORS['Data Center Electricity Use']],
            [0.75, REPORTING_SCOPE_COLORS['Both']],
            [1.0, REPORTING_SCOPE_COLORS['Both']]
        ],
        showscale=False
    )

    # Create legend traces
    legend_traces = [
        go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(size=10, color=color),
            name=name,
            showlegend=True
        )
        for name, color in REPORTING_SCOPE_COLORS.items()
    ]

    # Combine traces
    fig = go.Figure(data=[heatmap] + legend_traces)

    # Update layout
    fig.update_layout(
        title={
            'text': 'Electricity Usage Reporting Timeline',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 16}
        },
        xaxis_title='Reporting Year',
        yaxis_title='Company',
        xaxis={
            'side': 'bottom',
            'tickmode': 'array',
            'ticktext': [str(year) for year in years],
            'tickvals': years,
            'type': 'category'  # Force categorical axis
        },
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=600,
        margin=dict(l=150, r=50, t=100, b=50),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )

    return fig 