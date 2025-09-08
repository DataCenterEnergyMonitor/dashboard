import plotly.express as px
import pandas as pd
import hashlib


def create_energy_projections_line_plot(
    filtered_df, full_df=None, filters_applied=False
):
    """
    Create Energy projections line plot

    Args:
        filtered_df: DataFrame to display
        filters_applied: Boolean indicating if filters are actively applied
        full_df: unfiltered DataFrame
    """

    # Sort by company name for consistent ordering
    full_df = full_df.sort_values(["citation", "year"]).copy()
    filtered_df = filtered_df.sort_values(["citation", "year"]).copy()

    # Calculate y-axis range to avoid extra empty space
    ymin = filtered_df["energy_demand"].min() - 100
    ymax = filtered_df["energy_demand"].max() + 100

    # Calculate x-axis range to avoid extra empty space
    xmin = filtered_df["year"].min()
    xmax = full_df["year"].max()

    citation_list = full_df["citation"].unique()

    palette = px.colors.qualitative.Bold

    # Assign colors: brand color if available, else from palette
    color_map = {}
    palette_idx = 0
    color_map["citation"] = palette[palette_idx % len(palette)]

    if filtered_df.empty:
        return {
            "data": [],
            "layout": {
                "xaxis": {"title": "Year (Historical & Projection)", "visible": True},
                "yaxis": {"title": "Energy Demand (TWh)", "visible": True},
                "showlegend": False,
                "annotations": [
                    {
                        "text": "No data available for selected filters",
                        "xref": "paper",
                        "yref": "paper",
                        "x": 0.5,
                        "y": 0.5,
                        "showarrow": False,
                        "font": {"size": 16, "color": "gray"},
                    }
                ],
                "plot_bgcolor": "white",
            },
        }

    # Create fields for hover text
    def create_hover_text(df):
        """Process DataFrame fields for hover text display"""
        df["region"] = df["region"].apply(
            lambda x: f"Study Region: {x}<br>" if pd.notna(x) and str(x).strip() else ""
        )
        df["data_center_type_s_"] = df["data_center_type_s_"].apply(
            lambda x: f"Data Center Type(s): {x}<br>"
            if pd.notna(x) and str(x).strip()
            else ""
        )
        df["modeling_approach_es_"] = df["modeling_approach_es_"].apply(
            lambda x: f"Modeling Approach(es): {x}<br>"
            if pd.notna(x) and str(x).strip()
            else ""
        )
        df["time_horizon"] = df["time_horizon"].apply(
            lambda x: f"Time Horizon: {x}<br>" if pd.notna(x) and str(x).strip() else ""
        )
        df["label"] = df["label"].apply(
            lambda x: f"Scenario: {x}<br>" if pd.notna(x) and str(x).strip() else ""
        )

    custom_data = [
        "citation",
        "energy_demand",
        "year",
        "region",
        "data_center_type_s_",
        "modeling_approach_es_",
        "time_horizon",
        "label",
    ]

    filtered_df = filtered_df.copy()
    create_hover_text(filtered_df)

    # Create a combined grouping column for citation + label
    if "label" in filtered_df.columns:
        filtered_df["citation_label"] = (
            filtered_df["citation"] + " - " + filtered_df["label"].astype(str)
        )
    else:
        #filtered_df["citation_label"] = filtered_df["citation"]
        filtered_df = filtered_df.sort_values(["citation", "label", "year"]).copy()
    # Define line styles for different labels
    line_style_map = {
        "Historical": "solid",
        "Lower scenario": "dash",
        "Upper scenario": "dot",
    }
    # Create the line plot
    if filters_applied and "label" in filtered_df.columns:
        # Use the citation_label column you already created
        energy_projections_fig = px.line(
            filtered_df,
            x="year",
            y="energy_demand",
            color="citation",  # Keep color by citation
            markers=True,
            line_dash="label",  # Add line style by label

            color_discrete_map=color_map,
            labels={
                "year": "Year (Historical & Projection)",
                "energy_demand": "Energy Demand (TWh)",
                "citation": "Study",
                "label": "Scenario",
            },
            custom_data=custom_data,
        )
    else:
        # No filters applied
        energy_projections_fig = px.line(
            filtered_df,
            x="year",
            y="energy_demand",
            #markers=True,
            color=None,
            labels={
                "year": "Year (Historical & Projection)",
                "energy_demand": "Energy Demand (TWh)",
            },
            custom_data=custom_data,
        )

    if not filters_applied:
        energy_projections_fig.update_traces(
            line=dict(color="lightgray", width=2),
            opacity=0.5,
            #marker=dict(color="darkgray", size=5, opacity=0.5),
            showlegend=False,
        )
    else:
        energy_projections_fig.update_traces(
            marker=dict(size=6, opacity=0.7, line=dict(width=0.5, color="grey"))
        )

        # Add background traces to foreground figure
        if full_df is not None and len(full_df) > len(filtered_df):
            # Get citations that are in the filtered data
            filtered_citations = set(filtered_df["citation"].unique())

            # Filter background data to exclude companies already displayed
            background_df = full_df[
                ~full_df["citation"].isin(filtered_citations)
            ].copy()

            if (
                not background_df.empty
            ):  # Only create background if there are companies to show
                create_hover_text(background_df)

                background_fig = px.line(
                    background_df,
                    x="year",
                    y="energy_demand",
                    #markers=True,
                    custom_data=custom_data,
                )
                background_fig.update_traces(
                    line=dict(color="lightgray", width=2),
                    opacity=0.5,
                    #marker=dict(color="darkgray", size=5, opacity=0.5),
                    showlegend=False,
                )

                # Add to main figure
                for trace in background_fig.data:
                    energy_projections_fig.add_trace(trace)

                # Reorder so background appears behind colored data
                energy_projections_fig.data = (
                    energy_projections_fig.data[-len(background_fig.data) :]
                    + energy_projections_fig.data[: -len(background_fig.data)]
                )
    energy_projections_fig.update_xaxes(
        range=[xmin-1, xmax+1],
        # tickvals=[year_x_map[year] for year in years],
        # ticktext=[str(year) for year in years],
        showgrid=False,
        showline=True,
        linecolor="black",
        linewidth=1,
        title_font=dict(size=14),
    )

    energy_projections_fig.update_layout(
        font_family="Inter",
        plot_bgcolor="white",
        margin=dict(r=250),
        xaxis=dict(
            showgrid=False,  # disable gridlines
            dtick=1,  # force yearly intervals
            showline=True,
            linecolor="black",
            linewidth=1,
            title_font=dict(size=14),
        ),
        yaxis=dict(
            range=[
                filtered_df["energy_demand"].min()-50,
                filtered_df["energy_demand"].max()+50,
            ],
            showgrid=False,  # Disable gridlines
            showline=True,
            linecolor="black",
            linewidth=1,
            title_font=dict(size=14),
        ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            traceorder="normal",
        ),
        # margin=dict(t=100, b=100),  # set bottom margin for citation
        showlegend=filters_applied,
        template="simple_white",
    )

    for trace in energy_projections_fig.data:
        # If the trace represents a scenario, set its line_dash style
        label = getattr(trace, "name", None)
        if label and label in line_style_map:
            trace.line["dash"] = line_style_map[label]

    # Update marker size and hover template
    energy_projections_fig.update_traces(
        hovertemplate=(
            "<b>Publication: %{customdata[0]}</b><br>"
            + "Year: %{x}<br>"
            + "Energy Demand (TWh): %{y:.2f}<br>"
            # + "%{customdata[1]}<br>"
            # + "%{customdata[2]}<br>"
            + "%{customdata[3]}"
            + "%{customdata[4]}"
            + "%{customdata[5]}"
            + "<extra></extra>"
        )
    )
    return energy_projections_fig
