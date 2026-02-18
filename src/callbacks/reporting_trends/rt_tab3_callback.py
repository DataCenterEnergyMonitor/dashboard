import dash
from pathlib import Path
from dash import Input, Output, State, html
import json
from datetime import datetime
from components.excel_export import create_filtered_excel_download
from components.figure_card import create_figure_card

# Placeholder for water reporting heatmap - to be implemented
# For now, we'll create a simple placeholder figure


def get_rt_last_modified_date():
    """Get the last modified date for reporting data from metadata.json"""
    try:
        root_dir = Path(__file__).parent.parent.parent.parent
        json_path = root_dir / "data" / "dependencies" / "metadata.json"

        if not json_path.exists():
            return None

        with open(json_path, "r") as f:
            metadata = json.load(f)

        for file_info in metadata.get("files", []):
            if "reporting" in file_info.get("source_file", "").lower():
                last_modified = file_info.get("last_modified")
                if last_modified:
                    dt = datetime.fromisoformat(last_modified)
                    return dt.strftime("%B %d, %Y")

        return None
    except (FileNotFoundError, KeyError, ValueError) as e:
        print(f"Warning: Could not load last modified date: {e}")
        return None


def filter_data_by_year_range(df, from_year, to_year, year_col="reported_data_year"):
    """Filter dataframe by year range"""
    if df.empty:
        return df

    filtered_df = df.copy()

    if from_year is not None:
        filtered_df = filtered_df[filtered_df[year_col] >= from_year]

    if to_year is not None:
        filtered_df = filtered_df[filtered_df[year_col] <= to_year]

    return filtered_df


def filter_data_by_companies(df, companies, company_col="company_name"):
    """Filter dataframe by selected companies"""
    if df.empty or not companies:
        return df
    return df[df[company_col].isin(companies)]


# ID prefix for this page's components
ID_PREFIX = "rt-"


def register_rt_tab3_callbacks(app, reporting_df, pue_wue_companies_df=None):
    """Register callbacks for RT Tab 3 (Water Reporting heatmap).

    Filters are inside each tab. Filter values are synced via rt-filter-store
    so that switching tabs preserves the user's selections.
    """

    # Callback to update chart when filters or tab changes
    @app.callback(
        Output("rt-fig3-container", "children"),
        [
            Input(f"{ID_PREFIX}filter-store", "data"),
            Input(f"{ID_PREFIX}active-tab-store", "data"),
        ],
        prevent_initial_call=False,
    )
    def update_rt_tab3_chart(filter_data, active_tab):
        """Update the water reporting heatmap based on filter selections from store"""
        # Only process if we're on tab-3 (allow None for initial load)
        if active_tab is not None and active_tab != "tab-3":
            raise dash.exceptions.PreventUpdate

        # Get filter values from store
        from_year = None
        to_year = None
        companies = None

        if filter_data:
            from_year = (
                int(filter_data.get("from_year"))
                if filter_data.get("from_year")
                else None
            )
            to_year = (
                int(filter_data.get("to_year")) if filter_data.get("to_year") else None
            )
            companies = filter_data.get("companies")

        # Filter reporting_df by year range
        filtered_df = filter_data_by_year_range(reporting_df, from_year, to_year)

        # Filter by companies if selected
        filtered_df = filter_data_by_companies(filtered_df, companies)

        # TODO: Create water reporting heatmap chart
        # For now, return a placeholder
        import plotly.graph_objects as go

        fig = go.Figure()
        fig.add_annotation(
            text="Water Reporting Heatmap - Coming Soon",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20),
        )
        fig.update_layout(
            height=400,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )

        # Get last modified date for title
        last_modified_date = get_rt_last_modified_date()
        if last_modified_date:
            title = html.Div(
                [
                    html.Div("Water Reporting by Company Over Time"),
                    html.Div(
                        f"(as of {last_modified_date})",
                        style={
                            "fontSize": "0.85em",
                            "color": "#666",
                            "marginTop": "4px",
                        },
                    ),
                ]
            )
        else:
            title = "Water Reporting by Company Over Time"

        return html.Div(
            [
                html.A(id="rt-tab3-nav"),
                create_figure_card(
                    fig_id="rt-tab3-fig1",
                    title=title,
                    expand_id="expand-rt-tab3-fig1",
                    filename="water_reporting_heatmap",
                    figure=fig,
                    show_modebar=False,
                ),
            ],
            style={"margin": "35px 0"},
        )

    # Modal expand callback
    @app.callback(
        [
            Output("rt-fig3-modal", "is_open"),
            Output("rt-fig3-modal-title", "children"),
            Output("rt-fig3-expanded", "figure"),
        ],
        [Input("expand-rt-tab3-fig1", "n_clicks")],
        [
            State("rt-fig3-modal", "is_open"),
            State("rt-tab3-fig1", "figure"),
        ],
        prevent_initial_call=True,
    )
    def toggle_rt_tab3_modal(expand_clicks, is_open, current_figure):
        """Toggle the expanded modal view"""
        if not expand_clicks:
            raise dash.exceptions.PreventUpdate

        last_modified_date = get_rt_last_modified_date()
        if last_modified_date:
            modal_title = html.Div(
                [
                    html.Div("Water Reporting by Company Over Time"),
                    html.Div(
                        f"(as of {last_modified_date})",
                        style={
                            "fontSize": "0.85em",
                            "color": "#666",
                            "marginTop": "4px",
                        },
                    ),
                ]
            )
        else:
            modal_title = "Water Reporting by Company Over Time"

        return (
            not is_open,
            modal_title,
            current_figure or {},
        )

    # Download data callback
    @app.callback(
        Output("download-rt-tab3-fig1", "data"),
        Input("download-btn-rt-tab3-fig1", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_rt_tab3_data(n_clicks):
        """Download the reporting data as Excel"""
        root_dir = Path(__file__).parent.parent.parent.parent
        input_path = root_dir / "data" / "DCEWM-Reporting.xlsx"

        return create_filtered_excel_download(
            input_path=input_path,
            output_filename="water_reporting_data.xlsx",
            sheets_to_export=["Reporting", "Read Me"],
            internal_prefix="_internal_",
            n_clicks=n_clicks,
        )
