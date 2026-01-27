import plotly.graph_objects as go

# Update color palette with green shades and better contrast
REPORTING_SCOPE_COLORS = {
    'No Reporting': '#D9DDDC' ,#'rgba(255, 0, 0, 0.15)',  # Light gray '#D9DDDC' E0E0E0
    'Pending': '#EBF4DF',  # Chetwode Green '#F0FFF0' | '#F3F8E7'
    'Company Wide Electricity Use': '#6EC259',  # Gin Green | '#9DC183',
    'Data Center Fuel Use': '#337F1A',  # Granny Smith | '#337F1A'
    'Data Center Electricity Use':  '#1A6210' # Avocado Green | '#0B6623'
}
def create_energy_reporting_heatmap(filtered_df):
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

    # Print unique scopes to debug
    print("Unique scopes in data:", filtered_df['reporting_scope'].unique())
    
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
            
            if year_data.empty:
                value = 0
                text = f"{company} ({year})<br>No Reporting"
            else:
                # Get reporting status
                status = year_data['reporting_status'].iloc[0]
                
                # Handle pending submissions first
                if status == 'Pending data submission':
                    value = 0.1
                    text = f"{company} ({year})<br>Pending data submission"
                else:
                    # Get all scopes for this company/year
                    scopes = set(year_data['reporting_scope'].dropna().unique())
                    
                    # Debug print for specific company
                    if company == 'Salesforce':
                        print(f"Year {year} - Scopes: {scopes}")
                    
                    # Implement reporting hierarchy for reported data
                    if 'Data Center Electricity Use' in scopes:
                        value = 1.0
                        text = f"{company} ({year})<br>Reporting: Data Center Electricity Use"
                    elif 'Data Center Fuel Use' in scopes:
                        value = 0.7
                        text = f"{company} ({year})<br>Reporting: Data Center Fuel Use"
                    elif 'Company Wide Electricity Use' in scopes:
                        value = 0.4
                        text = f"{company} ({year})<br>Reporting: Company Wide Electricity Use"
                    else:
                        value = 0
                        text = f"{company} ({year})<br>No Reporting"
            
            row_data.append(value)
            row_hover.append(text)
        
        z_data.append(row_data)
        hover_texts.append(row_hover)

    # Create the heatmap trace with cell borders
    heatmap = go.Heatmap(
        z=z_data,
        x=years,
        y=companies,
        text=hover_texts,
        hoverongaps=False,
        hoverinfo='text',
        colorscale=[
            [0.0, REPORTING_SCOPE_COLORS['No Reporting']],     # No reporting
            [0.05, REPORTING_SCOPE_COLORS['No Reporting']],
            [0.05, REPORTING_SCOPE_COLORS['Pending']],         # Pending
            [0.15, REPORTING_SCOPE_COLORS['Pending']],
            [0.15, REPORTING_SCOPE_COLORS['Company Wide Electricity Use']],    # Energy Use
            [0.45, REPORTING_SCOPE_COLORS['Company Wide Electricity Use']],
            [0.45, REPORTING_SCOPE_COLORS['Data Center Fuel Use']], # Electricity Use
            [0.75, REPORTING_SCOPE_COLORS['Data Center Fuel Use']],
            [0.75, REPORTING_SCOPE_COLORS['Data Center Electricity Use']],   # Data Center
            [1.0, REPORTING_SCOPE_COLORS['Data Center Electricity Use']]
        ],
        showscale=False,
        xgap=1,  # Add small gaps between cells
        ygap=1   # Add small gaps between cells
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
        if name != 'Pending'  # Don't show pending in legend
    ]

    # Combine traces
    fig = go.Figure(data=[heatmap] + legend_traces)

    # Update layout
    fig.update_layout(
        # title={
        #     'text': 'Electricity Usage Reporting Timeline',
        #     'y': 0.95,
        #     'x': 0.5,
        #     'xanchor': 'center',
        #     'yanchor': 'top',
        #     'font': {'size': 16}
        # },
        xaxis_title='Reporting Year',
        yaxis_title='Company',
        xaxis={
            'side': 'bottom',
            'tickmode': 'array',
            'ticktext': [str(year) for year in years],
            'tickvals': years,
            'type': 'category',
            'showgrid': False,  # Disable default grid
            'linecolor': 'black',
            'linewidth': 1,
            'ticks': 'outside'
        },
        yaxis={
            'showgrid': False,  # Disable default grid
            'linecolor': 'black',
            'linewidth': 1,
            'ticks': 'outside'
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