import dash
from pathlib import Path
from dash import Dash, Input, Output, State, callback, dcc, html, callback_context
import pandas as pd
from charts.global_policies.stacked_area_chart import create_global_policies_stacked_area_plot
from components.excel_export import create_filtered_excel_download

def register_global_policies_area_callbacks():
    
    return fig