@app.callback(
    Output('wue-scatter-chart', 'figure'),
    [Input('filter-dropdown', 'value'),
    ]
)
def update_wue_scatter(filter_values):
    # Get the data
    data = app.wue_scatter_data
    df = data['df']
    
    fig = px.scatter(
    )
    
    return fig 