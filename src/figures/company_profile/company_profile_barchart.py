"""Horizontal bar chart comparing electricity usage across companies (Tab 3)."""

import plotly.graph_objects as go
import pandas as pd


def create_company_profile_bar_plot(df: pd.DataFrame) -> go.Figure:
    """Create a horizontal bar chart of electricity usage by company.

    Parameters
    ----------
    df : pd.DataFrame
        Energy-use dataframe with ``company_name``, ``electricity_usage_kwh``,
        ``reported_data_year``, and ``reporting_scope`` columns.
    """
    df["electricity_usage_kwh"] = pd.to_numeric(
        df["electricity_usage_kwh"], errors="coerce"
    )
    df = df.dropna(subset=["electricity_usage_kwh"])

    if df.empty:
        return go.Figure().update_layout(
            xaxis={"visible": False},
            yaxis={"visible": False},
            plot_bgcolor="white",
            paper_bgcolor="white",
            annotations=[
                {
                    "text": "No data available for selected filters",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 20},
                }
            ],
        )

    try:
        df["electricity_usage_billions"] = (
            df["electricity_usage_kwh"].astype(float) / 1e9
        )

        companies_order = (
            df[df["reporting_scope"] == "Company Wide Electricity Use"]
            .sort_values("electricity_usage_billions", ascending=False)[
                "company_name"
            ]
            .tolist()
        )

        if not companies_order:
            companies_order = (
                df[df["reporting_scope"] == "Data Center Electricity Use"]
                .sort_values("electricity_usage_billions", ascending=False)[
                    "company_name"
                ]
                .tolist()
            )

        num_companies = len(companies_order)
        if num_companies <= 3:
            bar_width = 0.1
        elif num_companies <= 6:
            bar_width = 0.35
        elif num_companies <= 10:
            bar_width = 0.45
        else:
            bar_width = 0.6

        fig = go.Figure()

        company_data = df[df["reporting_scope"] == "Company Wide Electricity Use"]
        if not company_data.empty:
            fig.add_trace(
                go.Bar(
                    y=company_data["company_name"],
                    x=company_data["electricity_usage_billions"],
                    name="Company Wide",
                    orientation="h",
                    marker_color="#00588D",
                    hovertemplate=(
                        "<b>%{y}</b><br>"
                        "Company Wide Usage: %{x:.1f}B kWh<br>"
                        "<extra></extra>"
                    ),
                    width=bar_width,
                )
            )

        dc_data = df[df["reporting_scope"] == "Data Center Electricity Use"]
        if not dc_data.empty:
            fig.add_trace(
                go.Bar(
                    y=dc_data["company_name"],
                    x=dc_data["electricity_usage_billions"],
                    name="Data Centers",
                    orientation="h",
                    marker_color="#3EBCD2",
                    opacity=0.7,
                    hovertemplate=(
                        "<b>%{y}</b><br>"
                        "Data Center Usage: %{x:.1f}B kWh<br>"
                        "<extra></extra>"
                    ),
                    width=bar_width,
                )
            )

        year = df["reported_data_year"].iloc[0] if not df.empty else "N/A"

        max_value = df["electricity_usage_billions"].max()
        tick_interval = 5 if max_value > 50 else 2

        fig.update_layout(
            title=None,
            xaxis_title="Electricity Usage (Billion kWh)",
            yaxis_title="Company",
            plot_bgcolor="white",
            paper_bgcolor="white",
            barmode="overlay",
            margin=dict(l=20, r=20, t=20, b=60),
            showlegend=True,
            legend_title=f"Reporting Scope ({year})",
            bargap=0.1,
            bargroupgap=0.05,
            xaxis={
                "type": "linear",
                "showgrid": True,
                "gridcolor": "lightgray",
                "side": "top",
                "dtick": tick_interval,
                "range": [0, max_value * 1.1],
            },
            yaxis={
                "automargin": True,
                "showgrid": False,
                "autorange": "reversed",
                "categoryorder": "array",
                "categoryarray": companies_order,
                "tickson": "boundaries",
                "ticklen": 0,
                "fixedrange": True,
                "constrain": "domain",
            },
        )

        return fig

    except Exception as e:
        print(f"Error creating chart: {str(e)}")
        import traceback

        traceback.print_exc()
        raise
