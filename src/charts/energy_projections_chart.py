import plotly.express as px
import pandas as pd


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

    # DEBUG: Filtered data summary
    print(f"\n=== FILTERED DATA ===")
    print(
        f"Shape: {filtered_df.shape}, Citations: {list(filtered_df['citation'].unique())}"
    )
    print("=== END FILTERED DATA ===\n")

    # Calculate y-axis range to avoid extra empty space
    ymin = full_df["energy_demand"].min() - 10
    ymax = full_df["energy_demand"].max() + 10

    # Calculate x-axis range to avoid extra empty space
    xmin = full_df["year"].min() - 1
    xmax = full_df["year"].max() + 1

    if full_df.empty:
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

    print(f"\n=== FILTERED DATA DEBUG ===")
    print(f"Filtered data shape: {filtered_df.shape}")
    print(f"Filtered citations: {filtered_df['citation'].unique()}")
    if "label" in filtered_df.columns:
        print(f"Filtered labels: {filtered_df['label'].unique()}")
        for citation in filtered_df["citation"].unique():
            citation_data = filtered_df[filtered_df["citation"] == citation]
            print(f"\n{citation} data:")
            for label in citation_data["label"].unique():
                label_data = citation_data[citation_data["label"] == label]
                print(f"  {label}: {len(label_data)} points")
    print("=== END FILTERED DATA DEBUG ===\n")

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

    # Always work with the full dataset
    plot_df = full_df.copy()
    create_hover_text(plot_df)

    # Create a combined grouping column for citation + label
    if "label" in plot_df.columns:
        plot_df["citation_label"] = (
            plot_df["citation"] + " - " + plot_df["label"].astype(str)
        )

    # Define line styles for different labels
    line_style_map = {
        "Historical": "solid",
        "Lower scenario": "dash",
        "Upper scenario": "dot",
    }

    citations = filtered_df["citation"].unique()
    palette = px.colors.qualitative.Dark24
    color_map = {
        citation: palette[i % len(palette)] for i, citation in enumerate(citations)
    }

    # Create the line plot with the full dataset
    energy_projections_fig = px.line(
        plot_df,
        x="year",
        y="energy_demand",
        color="citation",
        line_dash="label",
        markers=True,
        labels={
            "year": "Year (Historical & Projection)",
            "energy_demand": "Energy Demand (TWh)",
            "citation": "Study",
            "label": "Scenario",
        },
        color_discrete_map=color_map,
        custom_data=custom_data,
    )

    # DEBUG: Filtered traces only
    print(f"\n=== FILTERED TRACES ===")
    filtered_traces = [
        trace
        for trace in energy_projections_fig.data
        if any(citation in trace.name for citation in filtered_df["citation"].unique())
    ]
    print(f"Filtered traces: {len(filtered_traces)}")
    for i, trace in enumerate(filtered_traces):
        point_count = len(trace.x) if hasattr(trace, "x") and trace.x is not None else 0
        print(f"  {i}: {trace.name} ({point_count} points)")
    print("=== END FILTERED TRACES ===\n")

    # If filters are applied, determine which traces should be highlighted
    if filters_applied and not filtered_df.empty:
        # Create a set of tuples to identify which traces match the filter
        filtered_trace_keys = set()
        if "label" in filtered_df.columns:
            for _, row in filtered_df.iterrows():
                filtered_trace_keys.add((row["citation"], row["label"]))
        else:
            for citation in filtered_df["citation"].unique():
                # If no label column, add all labels for this citation
                citation_labels = plot_df[plot_df["citation"] == citation][
                    "label"
                ].unique()
                for label in citation_labels:
                    filtered_trace_keys.add((citation, label))

        # Update trace styling based on whether they match the filter
        for i, trace in enumerate(energy_projections_fig.data):
            # Extract citation and label from trace
            trace_citation = None
            trace_label = None

            # Plotly assigns trace names based on the color and line_dash variables
            # For color="citation", line_dash="label", the trace name follows pattern "citation, label"
            if hasattr(trace, "name") and trace.name:
                if ", " in trace.name:
                    trace_citation, trace_label = trace.name.split(", ", 1)
                else:
                    # Fallback: try to get from customdata
                    if (
                        hasattr(trace, "customdata")
                        and trace.customdata is not None
                        and len(trace.customdata) > 0
                    ):
                        trace_citation = trace.customdata[0][0]
                        trace_label_raw = trace.customdata[0][7]
                        if trace_label_raw and trace_label_raw.startswith("Scenario: "):
                            trace_label = trace_label_raw.replace(
                                "Scenario: ", ""
                            ).replace("<br>", "")

            # Debug print to see what we're getting
            if i < 3:
                print(
                    f"Trace {i}: name='{trace.name}', extracted citation='{trace_citation}', label='{trace_label}'"
                )

            # Check if this trace matches the filter
            trace_key = (trace_citation, trace_label)
            is_filtered = trace_key in filtered_trace_keys

            if is_filtered and i < 3:
                print(
                    f"Trace {i}: name='{trace.name}', extracted citation='{trace_citation}', label='{trace_label}'"
                )

    # If filters are applied, determine which traces should be highlighted
    if filters_applied and not filtered_df.empty:
        # Create a set of tuples to identify which traces match the filter
        filtered_trace_keys = set()
        if "label" in filtered_df.columns:
            for _, row in filtered_df.iterrows():
                filtered_trace_keys.add((row["citation"], row["label"]))
        else:
            for citation in filtered_df["citation"].unique():
                # If no label column, add all labels for this citation
                citation_labels = plot_df[plot_df["citation"] == citation][
                    "label"
                ].unique()
                for label in citation_labels:
                    filtered_trace_keys.add((citation, label))

        # Debug print to see what we're looking for
        print(f"Filtered trace keys to match: {filtered_trace_keys}")
        print(
            f"Sample filtered data labels: {filtered_df['label'].unique() if 'label' in filtered_df.columns else 'No label column'}"
        )

        # Update trace styling based on whether they match the filter
        for i, trace in enumerate(energy_projections_fig.data):
            # Extract citation and label from trace
            trace_citation = None
            trace_label = None

            # Plotly assigns trace names based on the color and line_dash variables
            # For color="citation", line_dash="label", the trace name follows pattern "citation, formatted_label"
            if hasattr(trace, "name") and trace.name:
                if ", " in trace.name:
                    trace_citation, trace_label_formatted = trace.name.split(", ", 1)
                    # Clean up the label - remove "Scenario: " prefix and "<br>" suffix
                    trace_label = trace_label_formatted.replace(
                        "Scenario: ", ""
                    ).replace("<br>", "")

            # Debug print for first few traces only to avoid spam
            if i < 6:
                print(
                    f"Trace {i}: name='{trace.name}', citation='{trace_citation}', cleaned_label='{trace_label}'"
                )

            # Check if this trace matches the filter
            trace_key = (trace_citation, trace_label)
            is_filtered = trace_key in filtered_trace_keys

            if i < 6:
                print(f"  -> trace_key={trace_key}, is_filtered={is_filtered}")

            if is_filtered:
                # This trace matches the filter - show in color with full hover
                energy_projections_fig.data[i].update(
                    marker=dict(
                        size=6, opacity=0.7, line=dict(width=0.5, color="grey")
                    ),
                    line=dict(width=2),
                    opacity=1.0,
                    showlegend=True,
                    hovertemplate=(
                        "<b>Publication: %{customdata[0]}</b><br>"
                        + "Year: %{x}<br>"
                        + "Energy Demand (TWh): %{y:.2f}<br>"
                        + "%{customdata[3]}"
                        + "%{customdata[4]}"
                        + "%{customdata[5]}"
                        + "<extra></extra>"
                    ),
                )
            else:
                # This trace doesn't match the filter - show in gray with minimal hover
                energy_projections_fig.data[i].update(
                    line=dict(color="lightgray", width=2),
                    opacity=0.4,
                    marker=dict(size=5, opacity=0.5),
                    showlegend=False,
                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>"
                        + "Year: %{x}<br>"
                        + "Energy Demand (TWh): %{y:.2f}<br>"
                        + "<extra></extra>"
                    ),
                )
    else:
        # No filters applied - show all traces in gray
        energy_projections_fig.update_traces(
            line=dict(color="lightgray", width=2),
            opacity=0.4,
            marker=dict(size=5, opacity=0.5),
            showlegend=False,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                + "Year: %{x}<br>"
                + "Energy Demand (TWh): %{y:.2f}<br>"
                + "<extra></extra>"
            ),
        )

    energy_projections_fig.update_xaxes(
        range=[xmin, xmax],
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
                ymin,
                ymax,
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
        showlegend=filters_applied,
        template="simple_white",
    )

    # Apply line dash styles
    for trace in energy_projections_fig.data:
        # Extract label from custom data if available
        if (
            hasattr(trace, "customdata")
            and trace.customdata is not None
            and len(trace.customdata) > 0
        ):
            label = trace.customdata[0][7]  # label is 8th custom data field
            if label and label.startswith("Scenario: "):
                clean_label = label.replace("Scenario: ", "").replace("<br>", "")
                if clean_label in line_style_map:
                    trace.line["dash"] = line_style_map[clean_label]

    # DEBUG: Final filtered traces
    print(f"\n=== FINAL FILTERED TRACES ===")
    final_filtered_traces = [
        trace
        for trace in energy_projections_fig.data
        if any(citation in trace.name for citation in filtered_df["citation"].unique())
    ]
    print(f"Final filtered traces: {len(final_filtered_traces)}")
    for i, trace in enumerate(final_filtered_traces):
        print(f"  {i}: {trace.name}")
    print("=== END FINAL FILTERED TRACES ===\n")

    return energy_projections_fig
