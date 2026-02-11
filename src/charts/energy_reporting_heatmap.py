import plotly.graph_objects as go
import plotly.io as pio

# Update color palette with green shades and better contrast
REPORTING_SCOPE_COLORS = {
    "No Reporting": "#D9DDDC",  # Light gray
    "Pending": "#EBF4DF",  # Chetwode Green
    "Company Wide Electricity Use": "#6EC259",  # Gin Green
    "Data Center Fuel Use": "#337F1A",  # Granny Smith
    "Data Center Electricity Use": "#1A6210",  # Avocado Green
}


def _display_value_for_year_data(year_data):
    """Map (company, year) rows to a single display value and heatmap z value.

    Display is driven by reporting_status so we never show a scope as reported
    when its status is "Pending Data Submission".

    - If any row has reporting_status equal to a scope
      ("Data Center Electricity Use", "Data Center Fuel Use",
      "Company Wide Electricity Use"), treat that as reported and show the
      highest-priority scope (Data Center Electricity > Fuel > Company Wide).
    - Else if any row has reporting_status == "Pending Data Submission",
      show Pending.
    - Else show No Reporting.
    """
    statuses = set(year_data["reporting_status"].dropna().unique())

    # Reported scopes: only where status equals the scope (not Pending / No Reporting)
    reported_scopes = statuses & {
        "Data Center Electricity Use",
        "Data Center Fuel Use",
        "Company Wide Electricity Use",
    }
    if reported_scopes:
        if "Data Center Electricity Use" in reported_scopes:
            return 1.0, "Data Center Electricity Use"
        if "Data Center Fuel Use" in reported_scopes:
            return 0.7, "Data Center Fuel Use"
        if "Company Wide Electricity Use" in reported_scopes:
            return 0.4, "Company Wide Electricity Use"
        return 0, "No Reporting"

    # No reported scopes: check for pending / no reporting
    if "Pending Data Submission" in statuses:
        return 0.1, "Pending Data Submission"
    if "No Reporting" in statuses:
        return 0, "No Reporting"
    return 0, "No Reporting"


def create_energy_reporting_heatmap(
    filtered_df,
    original_df=None,
    filters_applied=False,
    header_only=False,
    is_expanded=False,
):
    """Create a heatmap showing companies' reporting patterns over time.

    Args:
        filtered_df: The filtered dataframe for the current view
        original_df: Optional full dataframe to ensure all companies are shown
        filters_applied: If True, indicates filters have been applied
        header_only: If True, creates a minimal chart with just legend and x-axis at top
    """
    pio.templates.default = "simple_white"
    filtered_df = filtered_df.copy()

    if filtered_df.empty:
        if header_only:
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

    # Helper function to wrap company names at parentheses
    def wrap_company_name(name):
        """Wrap company name by moving parenthetical content to new line"""
        if "(" in name:
            parts = name.split("(", 1)
            return f"{parts[0].strip()}<br>({parts[1]}"
        return name

    # FIXED ROW HEIGHT - do not scale with container
    FIXED_ROW_HEIGHT = 25  # pixels per row

    df_for_companies = original_df if original_df is not None else filtered_df
    #companies = sorted(df_for_companies["company_name"].unique())
    companies = df_for_companies["company_name"].unique().tolist()
    years = sorted(filtered_df["reported_data_year"].unique())

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

        for company in companies:
            row_data = []
            row_hover = []

            for year in years:
                year_data = filtered_df[
                    (filtered_df["company_name"] == company)
                    & (filtered_df["reported_data_year"] == year)
                ]

                if year_data.empty:
                    value, display_label = 0, "No Reporting"
                else:
                    value, display_label = _display_value_for_year_data(year_data)

                if display_label in (
                    "Data Center Electricity Use",
                    "Data Center Fuel Use",
                    "Company Wide Electricity Use",
                ):
                    text = f"{company} ({year})<br>Reporting: {display_label}"
                else:
                    text = f"{company} ({year})<br>{display_label}"

                row_data.append(value)
                row_hover.append(text)

            z_data.append(row_data)
            hover_texts.append(row_hover)
            companies_display_wrapped.append(wrap_company_name(company))

        companies_display = companies_display_wrapped

    # Create the heatmap trace with cell borders
    heatmap = go.Heatmap(
        z=z_data,
        x=years,
        y=companies_display,
        text=hover_texts,
        hoverongaps=False,
        hoverinfo="skip" if header_only else "text",
        zmin=0.0,
        zmax=1.0,
        colorscale=[
            [0.0, REPORTING_SCOPE_COLORS["No Reporting"]],  # No reporting
            [0.05, REPORTING_SCOPE_COLORS["No Reporting"]],
            [0.05, REPORTING_SCOPE_COLORS["Pending"]],  # Pending
            [0.15, REPORTING_SCOPE_COLORS["Pending"]],
            [
                0.15,
                REPORTING_SCOPE_COLORS["Company Wide Electricity Use"],
            ],  # Energy Use
            [0.45, REPORTING_SCOPE_COLORS["Company Wide Electricity Use"]],
            [0.45, REPORTING_SCOPE_COLORS["Data Center Fuel Use"]],  # Electricity Use
            [0.75, REPORTING_SCOPE_COLORS["Data Center Fuel Use"]],
            [
                0.75,
                REPORTING_SCOPE_COLORS["Data Center Electricity Use"],
            ],  # Data Center
            [1.0, REPORTING_SCOPE_COLORS["Data Center Electricity Use"]],
        ],
        showscale=False,
        xgap=0.5,
        ygap=0.5,
        opacity=0 if header_only else 1,
    )

    # Create legend traces
    legend_items = {
        "No Reporting": REPORTING_SCOPE_COLORS["No Reporting"],
        "Pending Data Submission": REPORTING_SCOPE_COLORS["Pending"],
        "Company Wide Electricity Use": REPORTING_SCOPE_COLORS[
            "Company Wide Electricity Use"
        ],
        "Data Center Fuel Use": REPORTING_SCOPE_COLORS["Data Center Fuel Use"],
        "Data Center Electricity Use": REPORTING_SCOPE_COLORS[
            "Data Center Electricity Use"
        ],
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

    # Combine traces
    fig = go.Figure(data=[heatmap] + legend_traces)

    if header_only:
        fig_height = 120  # Cahnged from 180
        margin_config = dict(l=shared_left_margin, r=50, t=80, b=10)
        # margin_config = dict(
        #     l=shared_left_margin,
        #     r=50,
        #     t=110,
        #     b=40,
        # )
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
            "tickangle": 0,
            "fixedrange": True,
            "title": "",
            "range": [-0.5, len(years) - 0.5],
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
        # Minimal top margin
        # Calculate height based on actual number of filtered companies
        num_companies = len(companies_display)
        fig_height = (num_companies * FIXED_ROW_HEIGHT) + 40
        margin_config = dict(l=shared_left_margin, r=50, t=10, b=30)
        xaxis_config = {
            "side": "bottom",
            "tickmode": "array",
            "ticktext": [str(year) for year in years],
            "tickvals": years,
            "type": "category",
            "showgrid": False,
            "showticklabels": True if is_expanded else False,
            "showline": True if is_expanded else False,
            "ticks": "outside" if is_expanded else "",
            "tickfont": {"size": 12},
            "tickangle": 0,
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
            "fixedrange": False,  # enable scrolling on y-axis
            "categoryorder": "array",
            "categoryarray": companies_display  # the wrapped names list
        }
        show_legend = True if is_expanded else False
        legend_config = dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,1)",
            bordercolor=None,
            font={"size": 14},
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
        autosize=True,
    )

    return fig
