"""Bar chart showing energy usage over time for a single company (Tab 2)."""

import plotly.graph_objects as go
import pandas as pd

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


def create_company_energy_use_bar_plot(df):
    """Create a grouped bar chart of energy usage over time.

    Parameters
    ----------
    df : pd.DataFrame
        Company-filtered dataframe with ``reported_data_year``,
        ``electricity_usage_kwh``, and ``reporting_scope`` columns.
    """
    if df.empty:
        return _create_empty_chart("No data available")

    df = df.copy()
    df["electricity_usage_billions"] = (
        pd.to_numeric(df["electricity_usage_kwh"], errors="coerce") / 1e9
    )

    num_years = df["reported_data_year"].nunique()
    num_traces = df["reporting_scope"].nunique()
    min_year = df["reported_data_year"].min()
    max_year = df["reported_data_year"].max()

    bar_width = 0.8 / max(num_traces, 1)

    if num_traces == 1:
        if num_years <= 5:
            bar_width = min(bar_width, 0.4)
        elif num_years <= 10:
            bar_width = min(bar_width, 0.5)
        else:
            bar_width = min(bar_width, 0.7)

    if num_years <= 2:
        x_padding = 3.5
    elif num_years <= 4:
        x_padding = 1.5
    elif num_years <= 7:
        x_padding = 1.0
    elif num_years <= 12:
        x_padding = 0.7
    else:
        x_padding = 0.5

    fig = go.Figure()

    for scope in df["reporting_scope"].unique():
        scope_data = df[df["reporting_scope"] == scope]
        fig.add_trace(
            go.Bar(
                x=scope_data["reported_data_year"],
                y=scope_data["electricity_usage_billions"],
                name=scope,
                marker_color=REPORTING_SCOPE_COLORS.get(scope, "#999999"),
                width=bar_width,
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Usage: %{y:.1f}B kWh<br>"
                    f"Scope: {scope}<br>"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        barmode="group",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font_family="Inter",
        xaxis_title="Reporting Year",
        yaxis_title="Electricity Usage (Billion kWh)",
        xaxis=dict(
            tickmode="linear",
            dtick=1,
            range=[min_year - x_padding, max_year + x_padding],
            showgrid=False,
            showline=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="lightgray",
            showline=False,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title=None,
        ),
        margin=dict(t=80, b=60, l=60, r=20),
        bargap=0.2,
        bargroupgap=0.1,
        hovermode="x unified",
    )

    return fig
