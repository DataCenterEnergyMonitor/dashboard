import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc
from layouts.data_page_layout import create_data_page_layout
from components.filters.pue_wue_filters import create_filters


def create_pue_wue_page(app, pue_df, wue_df):
    content = dbc.Container(
        [
            html.H1("PUE and WUE Analysis"),
            create_filters(pue_df),  # Create filters for PUE
            html.Div(id="pue-wue-content"),  # Placeholder for PUE and WUE content
        ]
    )

    return create_data_page_layout(content)  # Use the base layout
