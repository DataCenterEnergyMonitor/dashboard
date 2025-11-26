import plotly.graph_objects as go
import plotly.io as pio

# Update color palette with green shades and better contrast
REPORTING_SCOPE_COLORS = {
    "no reporting evident": "#F5B9BF",
    "individual data center values only": "#6EC259",
    "fleet-wide values only": "#337F1A",
    "both fleet-wide and individual data center values": "#1A6210",
    "company not established": "#D9DDDC",
    "company Inactive": "#D9DDDC",
    "not yet released": "#EBF4DF",
}


def create_pue_wue_reporting_heatmap_plot(
    filtered_df,
    original_df=None,
    filters_applied=False,
    header_only=False,
    reporting_column="reports_pue",
):
    """Create a heatmap showing pue reporting patterns over time.

    Args:
        filtered_df: The filtered dataframe for the current view
        original_df: Optional full dataframe to ensure all companies are shown
        header_only: If True, creates a minimal chart with just legend and x-axis at top
        reporting_column: The column name to use for the reporting data "reports_pue" or "reports_wue"
    """

    pio.templates.default = "simple_white"
    filtered_df = filtered_df.copy()

    if filtered_df.empty:
        if header_only:
            # Return completely empty figure for header (nothing displayed)
            return {
                "data": [],
                "layout": {
                    "xaxis": {"visible": False},
                    "yaxis": {"visible": False},
                    "annotations": [
                        {
                            "text": "No data available for selected companies",
                            "xref": "paper",
                            "yref": "paper",
                            "x": 0.5,
                            "y": 0.5,
                            "showarrow": False,
                            "font": {"size": 16, "color": "gray"},
                        }
                    ],
                },
            }
        else:
            return {
                "data": [],
                "layout": {
                    "xaxis": {"visible": False},
                    "yaxis": {"visible": False},
                    "annotations": [
                        {
                            "text": "",
                            "xref": "paper",
                            "yref": "paper",
                            "showarrow": False,
                            "font": {"size": 20},
                        }
                    ],
                },
            }

    df_for_companies = original_df if original_df is not None else filtered_df
    companies = sorted(df_for_companies["company_name"].unique())
    years = sorted(filtered_df["year"].unique())

    # Helper function to wrap company names at parentheses
    def wrap_company_name(name):
        """Wrap company name by moving parenthetical content to new line"""
        if "(" in name:
            parts = name.split("(", 1)
            return f"{parts[0].strip()}<br>({parts[1]}"
        return name

    # FIXED ROW HEIGHT - do not scale with container
    FIXED_ROW_HEIGHT = 25  # pixels per row

    # Calculate dynamic left margin based on FILTERED companies
    if len(filtered_df) > 0:
        filtered_companies = sorted(filtered_df["company_name"].unique())
        max_company_name_length = (
            max(len(str(comp).split("(")[0].strip()) for comp in filtered_companies)
            if filtered_companies
            else 0
        )
        shared_left_margin = int(max(100, max_company_name_length * 5 + 20))
    else:
        shared_left_margin = 100

    # Find longest company name for dummy label in header
    if companies:
        longest_company = max(
            companies, key=lambda x: len(str(x).split("(")[0].strip())
        )
        dummy_label = wrap_company_name(longest_company)
    else:
        dummy_label = ""

    if header_only:
        # Create minimal chart with dummy y-labels that match the longest company name
        z_data = [[0.5] * len(years) for _ in range(3)]
        hover_texts = [[""] * len(years) for _ in range(3)]
        companies_display = [dummy_label, dummy_label, dummy_label]
    else:
        # Create full heatmap data with wrapped labels
        z_data = []
        hover_texts = []
        companies_display_wrapped = []

        for company_name in companies:
            row_data = []
            row_hover = []

            for year in years:
                year_data = filtered_df[
                    (filtered_df["company_name"] == company_name)
                    & (filtered_df["year"] == year)
                ]

                scopes = set(year_data[reporting_column].dropna().unique())

                if "company not established" in scopes:
                    value = 0.06
                    text = f"{company_name} ({year})<br>Company not established"
                elif "company Inactive" in scopes:
                    value = 0.01
                    text = f"{company_name} ({year})<br>Company inactive"
                elif "no reporting evident" in scopes:
                    value = 0.21
                    text = f"{company_name} ({year})<br>No reporting"
                elif "not yet released" in scopes:
                    value = 0.35
                    text = f"{company_name} ({year})<br>Not yet released"
                elif "both fleet-wide and individual data center values" in scopes:
                    value = 0.95
                    text = f"{company_name} ({year})<br>Reporting: fleet-wide and individual data center values"
                elif "fleet-wide values only" in scopes:
                    value = 0.8
                    text = (
                        f"{company_name} ({year})<br>Reporting: fleet-wide values only"
                    )
                elif "individual data center values only" in scopes:
                    value = 0.55
                    text = f"{company_name} ({year})<br>Reporting: individual data center values only"
                else:
                    value = 0.21
                    text = f"{company_name} ({year})<br>No Data"

                row_data.append(value)
                row_hover.append(text)

            z_data.append(row_data)
            hover_texts.append(row_hover)
            companies_display_wrapped.append(wrap_company_name(company_name))

        companies_display = companies_display_wrapped

    # Create the heatmap trace
    heatmap = go.Heatmap(
        z=z_data,
        x=years,
        y=companies_display,
        text=hover_texts,
        hoverongaps=False,
        hoverinfo="skip" if header_only else "text",
        colorscale=[
            [0.0, REPORTING_SCOPE_COLORS["company not established"]],
            [0.09, REPORTING_SCOPE_COLORS["company not established"]],
            [0.09, REPORTING_SCOPE_COLORS["company Inactive"]],
            [0.12, REPORTING_SCOPE_COLORS["company Inactive"]],
            [0.12, REPORTING_SCOPE_COLORS["no reporting evident"]],
            [0.30, REPORTING_SCOPE_COLORS["no reporting evident"]],
            [0.30, REPORTING_SCOPE_COLORS["not yet released"]],
            [0.40, REPORTING_SCOPE_COLORS["not yet released"]],
            [0.40, REPORTING_SCOPE_COLORS["individual data center values only"]],
            [0.70, REPORTING_SCOPE_COLORS["individual data center values only"]],
            [0.70, REPORTING_SCOPE_COLORS["fleet-wide values only"]],
            [0.90, REPORTING_SCOPE_COLORS["fleet-wide values only"]],
            [
                0.90,
                REPORTING_SCOPE_COLORS[
                    "both fleet-wide and individual data center values"
                ],
            ],
            [
                1.0,
                REPORTING_SCOPE_COLORS[
                    "both fleet-wide and individual data center values"
                ],
            ],
        ],
        showscale=False,
        xgap=0.5,
        ygap=0.5,
        opacity=0 if header_only else 1,
    )

    # Create legend traces
    legend_items = {
        "Not established": REPORTING_SCOPE_COLORS["company not established"],
        "No reporting": REPORTING_SCOPE_COLORS["no reporting evident"],
        "Individual DC only": REPORTING_SCOPE_COLORS[
            "individual data center values only"
        ],
        "Fleet-wide only": REPORTING_SCOPE_COLORS["fleet-wide values only"],
        "Fleet vs Individual DC": REPORTING_SCOPE_COLORS[
            "both fleet-wide and individual data center values"
        ],
        "Pending data submission": REPORTING_SCOPE_COLORS["not yet released"],
    }

    legend_traces = [
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(size=12, color=color, symbol="square"),
            name=name,
            showlegend=True,
        )
        for name, color in legend_items.items()
    ]

    fig = go.Figure(data=[heatmap] + legend_traces)

    if header_only:
        fig_height = 180
        margin_config = dict(
            l=shared_left_margin,
            r=50,
            t=110,
            b=40,
        )
        xaxis_config = {
            "side": "bottom",
            "tickmode": "array",
            "ticktext": [str(year) for year in years],
            "tickvals": years,
            "type": "category",
            "showgrid": False,
            "linecolor": "black",
            "linewidth": 1,
            "ticks": "outside",
            "tickfont": {"size": 12},
            "fixedrange": True,
            "title": "",
            "range": [-0.5, len(years) - 0.5],
            #'domain': [0, 1.0]
        }
        yaxis_config = {
            "visible": True,
            "showgrid": False,
            "showticklabels": True,
            "tickfont": {"size": 12, "color": "rgba(0,0,0,0)"},
            "ticks": "",
            "showline": False,
            "fixedrange": True,
            "range": [-0.5, 2.5],
        }
        show_legend = True
        legend_config = dict(
            orientation="h",
            yanchor="bottom",
            y=1.0,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,1)",
            bordercolor=None,
            font={"size": 14},
            itemsizing="constant",
            tracegroupgap=5,
        )
    else:
        # Calculate height based on actual number of filtered companies
        num_companies = len(companies_display)
        fig_height = num_companies * FIXED_ROW_HEIGHT + 100

        margin_config = dict(
            l=shared_left_margin,
            r=50,
            t=10,
            b=40,
        )
        xaxis_config = {
            "side": "bottom",
            "tickmode": "array",
            "ticktext": [str(year) for year in years],
            "tickvals": years,
            "type": "category",
            "showgrid": False,
            "showticklabels": True,
            "showline": False,
            "ticks": "outside",
            "tickfont": {"size": 12},
            "fixedrange": True,
            "range": [-0.5, len(years) - 0.5],
        }
        yaxis_config = {
            "showgrid": False,
            "linecolor": "black",
            "linewidth": 1,
            "ticks": "outside",
            "tickfont": {"size": 12},
            "autorange": "reversed",
            "fixedrange": False,
        }
        show_legend = False
        legend_config = dict(
            orientation="h",
            yanchor="top",
            y=1.0,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,1)",
            bordercolor=None,
            font={"size": 12},
            itemsizing="constant",
            tracegroupgap=5,
        )

    fig.update_layout(
        xaxis=xaxis_config,
        yaxis=yaxis_config,
        plot_bgcolor="rgba(0,0,0,0)" if header_only else "white",
        paper_bgcolor="white",
        height=fig_height,
        margin=margin_config,
        showlegend=show_legend,
        legend=legend_config,
        autosize=False,
    )

    return fig
