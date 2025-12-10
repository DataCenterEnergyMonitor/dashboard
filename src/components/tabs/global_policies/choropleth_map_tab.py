from dash import html


def create_choropleth_map_tab(app, globalpolicies_df):
    # Return just the content, not the full layout (layout is handled by parent)
    return html.H4(
        "Coming soon...",
        style={
            "width": "50%",
            "margin": "0 auto",
            "textAlign": "center",
            "paddingTop": "50px",
        },
    )
