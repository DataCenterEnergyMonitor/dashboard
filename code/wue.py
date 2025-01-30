# import libraries
import pandas as pd
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import janitor
import dash
from dash import dcc, html, Input, Output

### Import Data

# import WUE data
# define relative path
relative_path = Path('../data/dc_energy_use_pue.xlsx')

# get absolute path
absolute_path = relative_path.resolve()
print(absolute_path)

# import IAC database excell
# set skiprows=1 to start data import from the second row
wue_df = pd.read_excel(relative_path, sheet_name='Input - WUE', skiprows=1) 

# format header values into a snake case
wue_df = wue_df.clean_names()

import dash
from dash import html, dcc
import plotly.express as px
from dash.dependencies import Input, Output

# Calculate top 5 companies with the most occurrences
company_counts = wue_df["company"].value_counts().head(5).index.tolist()

import dash
from dash import html, dcc
import plotly.express as px
from dash.dependencies import Input, Output

# Calculate top 5 companies with the most occurrences
company_counts = wue_df["company"].value_counts().head(5).index.tolist()

# Calculate global industry average outside the callback
#global_industry_avg = wue_df.groupby('applicable_year')['wue'].mean().reset_index()
global_industry_avg = {
    'applicable_year': wue_df['applicable_year'],  # The list of years from your DataFrame
    'wue': [1.8] * len(wue_df['applicable_year'])   # The same WUE value for all years
}



# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=['https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap']
)
server = app.server

# Custom CSS for Roboto font and improved styling
app.layout = html.Div([
    html.H1(
        "Data Center Water Usage Effectiveness (WUE): Trends by Company",
        style={'fontFamily': 'Roboto', 'fontWeight': '500', 'marginBottom': '30px'}
    ),
    
    # Description of WUE with constrained width and darker gray color
    html.Div([
        html.P(
            "Water Usage Effectiveness (WUE) is a ratio that measures how efficiently a data center uses water.",
            style={
                'fontFamily': 'Roboto',
                'marginBottom': '20px',
                'color': '#404040',
                'maxWidth': '800px'  # Matches title width approximately
            }
        )
    ]),
    
    # Filters section
    html.Div([
        html.Label("Facility Scope:", style={'fontFamily': 'Roboto', 'fontWeight': '500'}),
        dcc.Dropdown(
            id='facility-scope-dropdown',
            options=[
                {"label": scope, "value": scope} for scope in wue_df["facility_scope"].dropna().unique()
            ],
            value=wue_df["facility_scope"].dropna().unique()[0],
            placeholder="Select a facility scope",
            style={'fontFamily': 'Roboto'}
        ),
    ], style={"marginBottom": "20px", "width": "100%"}),
    
    html.Div([
        html.Label("Company:", style={'fontFamily': 'Roboto', 'fontWeight': '500'}),
        dcc.Dropdown(
            id='company-dropdown',
            options=[
                {"label": "All", "value": "All"}
            ] + [
                {"label": company, "value": company} for company in wue_df["company"].unique()
            ],
            multi=True,
            value=company_counts,
            placeholder="Select a company",
            style={'fontFamily': 'Roboto'}
        ),
    ], style={"marginBottom": "20px", "width": "100%"}),
    
    # Download button with improved styling and larger font
    html.Div([
        html.Button(
            "Download Data",
            id="download-button",
            n_clicks=0,
            style={
                'backgroundColor': '#4CAF50',
                'color': 'white',
                'padding': '12px 24px',
                'border': 'none',
                'borderRadius': '4px',
                'cursor': 'pointer',
                'fontFamily': 'Roboto',
                'fontWeight': '500',
                'fontSize': '14px',  # Matches filter label size
                'width': '200px'
            }
        ),
        dcc.Download(id="download-dataframe"),
    ], style={"textAlign": "right", "marginBottom": "20px"}),
    
    dcc.Graph(id='scatter-chart')
], style={'padding': '20px', 'maxWidth': '1200px', 'margin': 'auto'})

@app.callback(
    [Output('scatter-chart', 'figure'),
     Output('company-dropdown', 'value')],
    [Input('company-dropdown', 'value'),
     Input('facility-scope-dropdown', 'value')]
)
def update_chart(selected_companies, selected_scope):
    filtered_df = wue_df.dropna(subset=["facility_scope"])

    if selected_companies and "All" in selected_companies and len(selected_companies) > 1:
        selected_companies.remove("All")

    if selected_companies:
        if "All" in selected_companies:
            pass
        else:
            filtered_df = filtered_df[filtered_df["company"].isin(selected_companies)]

    if selected_scope:
        filtered_df = filtered_df[filtered_df["facility_scope"] == selected_scope]

    # Create the main scatter plot
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

    # Add global industry average line with green color
    wue_fig.add_scatter(
        x=global_industry_avg['applicable_year'],
        y=global_industry_avg['wue'],
        mode='lines',
        name='Industry Average',
        line=dict(color='#2E8B57', dash='dash', width=2),  # Sea green color
        hovertemplate='Year: %{x}<br>Industry Avg WUE: %{y:.2f}<extra></extra>'
    )
    wue_fig.update_layout(
    font_family="Roboto",
    plot_bgcolor='white',
    xaxis=dict(
        showgrid=False,  # Disable gridlines
        dtick=1,  # Force yearly intervals
        showline=True,
        linecolor='black',
        linewidth=1,
        title_font=dict(size=14)
    ),
    yaxis=dict(
        showgrid=False,  # Disable gridlines
        range=[0, max(filtered_df['wue'].max() * 1.1, 1.8)],  # Start at 0
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
        margin=dict(t=100, b=100),  # Increased bottom margin for citation
        showlegend=True,
        template='simple_white'
    )

    # Increase marker size
    wue_fig.update_traces(marker=dict(size=10), selector=dict(mode='markers'))

    # Add source citation with lower position
    wue_fig.add_annotation(
        text="Source: [TBD]",
        xref="paper",
        yref="paper",
        x=0,
        y=-0.2,  # Moved lower
        showarrow=False,
        font=dict(size=10),
        align="left"
    )

    return wue_fig, selected_companies

# Download callback remains the same
@app.callback(
    Output("download-dataframe", "data"),
    [Input("download-button", "n_clicks"),
     Input('company-dropdown', 'value'),
     Input('facility-scope-dropdown', 'value')]
)
def download_data(n_clicks, selected_companies, selected_scope):
    if not n_clicks or dash.callback_context.triggered_id != 'download-button':
        return dash.no_update

    filtered_df = wue_df.dropna(subset=["facility_scope"])

    if selected_companies and "All" in selected_companies and len(selected_companies) > 1:
        selected_companies.remove("All")

    if selected_companies:
        if "All" in selected_companies:
            pass
        else:
            filtered_df = filtered_df[filtered_df["company"].isin(selected_companies)]

    if selected_scope:
        filtered_df = filtered_df[filtered_df["facility_scope"] == selected_scope]

    return dcc.send_data_frame(filtered_df.to_csv, "filtered_data.csv")

if __name__ == "__main__":
    app.run_server(debug=True, port=8053)