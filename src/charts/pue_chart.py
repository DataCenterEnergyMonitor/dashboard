import plotly.express as px
from .styles import get_pue_chart_layout

def create_pue_scatter_plot(filtered_df, selected_scope, industry_avg):
    """
    Creates a PUE scatter plot with company data points and industry average line.
    
    Args:
        filtered_df: DataFrame with PUE data
        selected_scope: String indicating facility scope ('fleet-wide' or "single location")
        global_industry_avg: DataFrame with industry average PUE values
        
    Returns:
        Plotly figure object
    """
    pue_fig = px.scatter(
        filtered_df,
        x='applicable_year',
        y='real_pue',
        color='company',
        labels={
            "applicable_year": "Year",
            "real_pue": "Power Usage Effectiveness (PUE)",
            "company": "Company Name",
            "geographical_scope": "Location"
        }
    )
    
    # Add connecting lines if facility scope is fleet-wide
    if selected_scope == "fleet-wide":
        for company in filtered_df['company'].unique():
            company_data = filtered_df[filtered_df['company'] == company].sort_values('applicable_year')
            pue_fig.add_scatter(
                x=company_data['applicable_year'],
                y=company_data['real_pue'],
                mode='lines',
                line=dict(width=1),
                showlegend=False,
                hoverinfo='skip',
                line_color=px.colors.qualitative.Set2[list(filtered_df['company'].unique()).index(company) % len(px.colors.qualitative.Set2)]
            )

    # Add global industry average line
    pue_fig.add_scatter(
        x=industry_avg['applicable_year'],
        y=industry_avg['real_pue'],
        mode='lines',
        name='Industry Average',
        line=dict(color='#bbbbbb', dash='dash', width=2),
        hovertemplate='Year: %{x}<br>Industry Avg PUE: %{y:.2f}<extra></extra>'
    )

    # Apply layout settings
    pue_fig.update_layout(get_pue_chart_layout(filtered_df))

    # Update marker size
    pue_fig.update_traces(marker=dict(size=10), selector=dict(mode='markers'))
    
    # Add source citation
    pue_fig.add_annotation(
        text="Source: [TBD]",
        xref="paper",
        yref="paper",
        x=0,
        y=-0.2,
        showarrow=False,
        font=dict(size=10),
        align="left"
    )

    return pue_fig
