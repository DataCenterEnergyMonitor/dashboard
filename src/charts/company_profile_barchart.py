import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from .styles import get_bar_chart_layout
from data_loader import load_company_profile_data
import math

current_reporting_year = datetime.now().year - 1
previous_reporting_year = current_reporting_year - 1

# Define color palette for reporting scopes
REPORTING_SCOPE_COLORS = {
    "Company Wide Electricity Use": "rgba(23, 79, 138, 0.8)",
    "Data Center Electricity Use": "#3EBCD2",
}


def create_company_profile_bar_plot(df: pd.DataFrame) -> go.Figure:
    """
    Create a horizontal bar chart showing electricity usage by company and reporting scope.

    Args:
        df (pd.DataFrame): Filtered dataframe containing energy usage data

    Returns:
        go.Figure: Plotly figure object with horizontal bars showing energy usage
    """
    print("Creating energy use bar plot")

    # Ensure electricity_usage_kwh is numeric
    df["electricity_usage_kwh"] = pd.to_numeric(
        df["electricity_usage_kwh"], errors="coerce"
    )

    # Remove rows with NaN values
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
        # Convert to billions for better readability
        df["electricity_usage_billions"] = (
            df["electricity_usage_kwh"].astype(float) / 1e9
        )

        # Sort companies by company-wide electricity usage (descending)
        companies_order = (
            df[df["reporting_scope"] == "Company Wide Electricity Use"]
            .sort_values("electricity_usage_billions", ascending=False)["company_name"]
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

        fig = go.Figure()

        # Add company-wide bars first
        company_data = df[df["reporting_scope"] == "Company Wide Electricity Use"]
        if not company_data.empty:
            fig.add_trace(
                go.Bar(
                    y=company_data["company_name"],
                    x=company_data["electricity_usage_billions"],
                    name="Company Wide",
                    orientation="h",
                    marker_color="#00588D",
                    hovertemplate="<b>%{y}</b><br>"
                    + "Company Wide Usage: %{x:.1f}B kWh<br>"
                    + "<extra></extra>",
                    width=0.8,
                )
            )

        # Add data center bars
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
                    hovertemplate="<b>%{y}</b><br>"
                    + "Data Center Usage: %{x:.1f}B kWh<br>"
                    + "<extra></extra>",
                    width=0.8,
                )
            )

        # Get the selected year
        year = df["reported_data_year"].iloc[0] if not df.empty else "N/A"

        # Calculate max value for x-axis
        max_value = df["electricity_usage_billions"].max()
        tick_interval = 5 if max_value > 50 else 2

        # Calculate dynamic height based on number of companies
        num_companies = len(companies_order)
        min_height_per_company = 30  # Minimum pixels per company
        margin_height = 100  # Space for margins, title, etc.
        total_height = max(400, num_companies * min_height_per_company + margin_height)

        # Update layout
        fig.update_layout(
            title=None,
            xaxis_title="Electricity Usage (Billion kWh)",
            yaxis_title="Company",
            plot_bgcolor="white",
            paper_bgcolor="white",
            barmode="overlay",
            height=total_height,
            margin=dict(l=20, r=20, t=40, b=20),
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


def create_company_energy_use_bar_plot(df: pd.DataFrame) -> go.Figure:
    """
    Create a bar chart showing energy usage over time for companies.

    Args:
        df (pd.DataFrame): DataFrame containing energy usage data with columns:
            - company_name
            - reported_data_year
            - electricity_usage_kwh
            - reporting_scope
    """
    if df.empty:
        return create_empty_chart("No data available")

    try:
        # Convert electricity_usage_kwh to numeric and billions
        df["electricity_usage_billions"] = (
            pd.to_numeric(df["electricity_usage_kwh"], errors="coerce") / 1e9
        )

        # Create the figure
        fig = go.Figure()

        # Add bars for each reporting scope
        for scope in df["reporting_scope"].unique():
            scope_data = df[df["reporting_scope"] == scope]

            fig.add_trace(
                go.Bar(
                    x=scope_data["reported_data_year"],
                    y=scope_data["electricity_usage_billions"],
                    name=scope,
                    marker_color=REPORTING_SCOPE_COLORS.get(scope, "#999999"),
                    width=0.4,  # Set fixed bar width
                    hovertemplate=(
                        "<b>%{x}</b><br>"
                        "Usage: %{y:.1f}B kWh<br>"
                        f"Scope: {scope}<br>"
                        "<extra></extra>"
                    ),
                )
            )

        # Update layout
        fig.update_layout(
            title=None,
            xaxis_title="Reporting Year",
            yaxis_title="Electricity Usage (Billion kWh)",
            plot_bgcolor="white",
            paper_bgcolor="white",
            barmode="group",
            bargap=0.2,
            bargroupgap=0,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
                font=dict(
                    family="Inter",
                    size=12,
                ),
            ),
            legend_title=None,
            xaxis=dict(
                showgrid=False,
                gridwidth=1,
                gridcolor="lightgray",
                tickmode="linear",
                range=[
                    df["reported_data_year"].min() - 0.5,
                    df["reported_data_year"].max() + 0.5,
                ],  # Add padding to x-axis
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor="lightgray",
                zeroline=True,
                zerolinewidth=1,
                zerolinecolor="lightgray",
            ),
            margin=dict(t=50, r=20, b=20, l=20),
        )

        return fig

    except Exception as e:
        print(f"Error in create_company_energy_use_bar_plot: {str(e)}")
        import traceback

        traceback.print_exc()
        return create_empty_chart(f"Error creating chart: {str(e)}")
