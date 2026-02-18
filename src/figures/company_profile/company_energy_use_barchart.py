"""Bar chart showing energy usage over time for a single company (Tab 2)."""

import plotly.graph_objects as go
import pandas as pd
from ..styles import get_bar_chart_layout

REPORTING_SCOPE_COLORS = {
    "Company Wide Electricity Use": "#00588D",
    "Data Center Electricity Use": "#3EBCD2",
}


def _create_empty_chart(message):
    return go.Figure().update_layout(
        xaxis={"visible": False},
        yaxis={"visible": False},
        plot_bgcolor="white",
        paper_bgcolor="white",
        annotations=[
            {
                "text": message,
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 20},
            }
        ],
    )


def create_company_energy_use_bar_plot(df: pd.DataFrame) -> go.Figure:
    """Create a grouped bar chart of energy usage over time.

    Parameters
    ----------
    df : pd.DataFrame
        Company-filtered dataframe with ``reported_data_year``,
        ``electricity_usage_kwh``, and ``reporting_scope`` columns.
    """
    if df.empty:
        return _create_empty_chart("No data available")

    try:
        df["electricity_usage_billions"] = (
            pd.to_numeric(df["electricity_usage_kwh"], errors="coerce") / 1e9
        )

        num_years = df["reported_data_year"].nunique()
        num_traces = df["reporting_scope"].nunique()
        min_year = df["reported_data_year"].min()
        max_year = df["reported_data_year"].max()

        # Single scope  → explicit width to cap bar size
        # Multiple scopes → no width, let bargap/bargroupgap auto-size
        if num_traces <= 1:
            if num_years <= 5:
                bar_width = 0.4
            elif num_years <= 10:
                bar_width = 0.5
            else:
                bar_width = 0.7
        else:
            bar_width = None

        # Dynamic x-axis padding
        if num_years <= 2:
            x_padding = 3.5
        elif num_years <= 4:
            x_padding = 1.5
        elif num_years <= 7:
            x_padding = 1.0
        elif num_years <= 12:
            x_padding = 0.7
        else:
            x_padding = 0.6

        fig = go.Figure()

        for scope in df["reporting_scope"].unique():
            scope_data = df[df["reporting_scope"] == scope]
            trace_kwargs = dict(
                x=scope_data["reported_data_year"],
                y=scope_data["electricity_usage_billions"],
                name=scope,
                marker_color=REPORTING_SCOPE_COLORS.get(scope, "#999999"),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Usage: %{y:.1f}B kWh<br>"
                    f"Scope: {scope}<br>"
                    "<extra></extra>"
                ),
            )
            if bar_width is not None:
                trace_kwargs["width"] = bar_width
            fig.add_trace(go.Bar(**trace_kwargs))

        # Apply shared bar-chart base layout (template, margins, legend)
        fig.update_layout(barmode="group")
        fig.update_layout(get_bar_chart_layout())

        # Override with chart-specific settings
        layout_overrides = dict(
            xaxis_title="Reporting Year",
            yaxis_title="Electricity Usage (Billion kWh)",
            yaxis=dict(tickmode="auto", dtick=None),
            xaxis=dict(
                tickmode="linear",
                range=[min_year - x_padding, max_year + x_padding],
            ),
            bargap=0.2,
        )
        if bar_width is None:
            layout_overrides["bargroupgap"] = 0
        fig.update_layout(**layout_overrides)

        return fig

    except Exception as e:
        print(f"Error in create_company_energy_use_bar_plot: {str(e)}")
        import traceback

        traceback.print_exc()
        return _create_empty_chart(f"Error creating chart: {str(e)}")
