import plotly.express as px
from .styles import get_common_chart_layout

def create_wue_scatter_plot(filtered_df, selected_scope, industry_avg):
    wue_fig = px.scatter(
        filtered_df,
        x='applicable_year',
        y='wue',
        color='company',
        labels={
            "applicable_year": "Year",
            "wue": "Water Usage Effectiveness (WUE)",
            "company": "Company Name"
        }
    )
    
    # Add connecting lines if facility scope is fleet-wide
    if selected_scope == "fleet-wide":
        for company in filtered_df['company'].unique():
            company_data = filtered_df[filtered_df['company'] == company].sort_values('applicable_year')
            wue_fig.add_scatter(
                x=company_data['applicable_year'],
                y=company_data['wue'],
                mode='lines',
                line=dict(width=1),
                showlegend=False,
                hoverinfo='skip',
                line_color=px.colors.qualitative.Set2[list(filtered_df['company'].unique()).index(company) % len(px.colors.qualitative.Set2)]
            )

    # Add global industry average line
    wue_fig.add_scatter(
        x=industry_avg['applicable_year'],
        y=industry_avg['wue'],
        mode='lines',
        name='Industry Average',
        line=dict(color='#bbbbbb', dash='dash', width=2),
        hovertemplate='Year: %{x}<br>Industry Avg WUE: %{y:.2f}<extra></extra>'
    )

    # Apply layout settings
    wue_fig.update_layout(get_common_chart_layout())

    # Update marker size
    wue_fig.update_traces(marker=dict(size=10), selector=dict(mode='markers'))
    
    # Add source citation
    wue_fig.add_annotation(
        text="Source: [TBD]",
        xref="paper",
        yref="paper",
        x=0,
        y=-0.2,
        showarrow=False,
        font=dict(size=10),
        align="left"
    )

    return wue_fig
