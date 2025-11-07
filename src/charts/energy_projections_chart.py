# import plotly.express as px
# import pandas as pd


# def create_energy_projections_line_plot(
#     filtered_df,
#     full_df=None,
#     filters_applied=False,
#     yaxis_title="Energy Demand (TWh)",
#     y_label="Energy Demand (TWh)"
# ):
#     """
#     Create Energy projections line plot

#     Args:
#         filtered_df: DataFrame to display
#         filters_applied: Boolean indicating if filters are actively applied
#         full_df: unfiltered DataFrame
#     """

#     # Sort by company name for consistent ordering
#     full_df = full_df.sort_values(["citation", "year"]).copy()
#     filtered_df = filtered_df.sort_values(["citation", "year"]).copy()

#     # # DEBUG: Filtered data summary
#     # print(f"\n=== FILTERED DATA ===")
#     # print(
#     #     f"Shape: {filtered_df.shape}, Citations: {list(filtered_df['citation'].unique())}"
#     # )
#     # print("=== END FILTERED DATA ===\n")

#     # Calculate y-axis range to avoid extra empty space
#     ymin = full_df["energy_demand"].min() - 10
#     ymax = full_df["energy_demand"].max() + 10

#     # Calculate x-axis range to avoid extra empty space
#     xmin = full_df["year"].min() - 1
#     xmax = full_df["year"].max() + 1

#     if full_df.empty:
#         return {
#             "data": [],
#             "layout": {
#                 "xaxis": {"title": "Year", "visible": True},
#                 "yaxis": {"title": yaxis_title, "visible": True},
#                 "showlegend": False,
#                 "annotations": [
#                     {
#                         "text": "No data available for selected filters",
#                         "xref": "paper",
#                         "yref": "paper",
#                         "x": 0.5,
#                         "y": 0.5,
#                         "showarrow": False,
#                         "font": {"size": 16, "color": "gray"},
#                     }
#                 ],
#                 "plot_bgcolor": "white",
#             },
#         }

#     # print(f"\n=== FILTERED DATA DEBUG ===")
#     # print(f"Filtered data shape: {filtered_df.shape}")
#     # print(f"Filtered citations: {filtered_df['citation'].unique()}")
#     # if "label" in filtered_df.columns:
#     #     print(f"Filtered labels: {filtered_df['label'].unique()}")
#     #     for citation in filtered_df["citation"].unique():
#     #         citation_data = filtered_df[filtered_df["citation"] == citation]
#     #         print(f"\n{citation} data:")
#     #         for label in citation_data["label"].unique():
#     #             label_data = citation_data[citation_data["label"] == label]
#     #             print(f"  {label}: {len(label_data)} points")
#     # print("=== END FILTERED DATA DEBUG ===\n")

#     # Create fields for hover text
#     def create_hover_text(df):
#         """Process DataFrame fields for hover text display"""
#         df["region"] = df["region"].apply(
#             lambda x: f"Study Region: {x}<br>" if pd.notna(x) and str(x).strip() else ""
#         )
#         df["data_center_type_s_"] = df["data_center_type_s_"].apply(
#             lambda x: f"Data Center Type(s): {x}<br>"
#             if pd.notna(x) and str(x).strip()
#             else ""
#         )
#         df["modeling_approach_es_"] = df["modeling_approach_es_"].apply(
#             lambda x: f"Modeling Approach(es): {x}<br>"
#             if pd.notna(x) and str(x).strip()
#             else ""
#         )
#         df["time_horizon"] = df["time_horizon"].apply(
#             lambda x: f"Time Horizon: {x}<br>" if pd.notna(x) and str(x).strip() else ""
#         )
#         df["label"] = df["label"].apply(
#             lambda x: f"Scenario: {x}<br>" if pd.notna(x) and str(x).strip() else ""
#         )

#     custom_data = [
#         "citation",
#         "energy_demand",
#         "year",
#         "region",
#         "data_center_type_s_",
#         "modeling_approach_es_",
#         "time_horizon",
#         "label",
#     ]

#     # Always work with the full dataset
#     plot_df = full_df.copy()
#     create_hover_text(plot_df)

#     # Create a combined grouping column for citation + label
#     if "label" in plot_df.columns:
#         plot_df["citation_label"] = (
#             plot_df["citation"] + " - " + plot_df["label"].astype(str)
#         )

#     # Define line styles for different labels
#     line_style_map = {
#         "Historical": "solid",
#         "Lower scenario": "dash",
#         "Upper scenario": "dot",
#     }

#     citations = filtered_df["citation"].unique()
#     palette = px.colors.qualitative.Dark24
#     color_map = {
#         citation: palette[i % len(palette)] for i, citation in enumerate(citations)
#     }

#     # Create the line plot with the full dataset
#     energy_projections_fig = px.line(
#         plot_df,
#         x="year",
#         y="energy_demand",
#         color="citation",
#         line_dash="label",
#         markers=True,
#         labels={
#             "year": "Year",
#             "energy_demand": y_label,
#             "citation": "Study",
#             "label": "Scenario",
#         },
#         color_discrete_map=color_map,
#         custom_data=custom_data,
#     )

#     # # DEBUG: Filtered traces only
#     # print(f"\n=== FILTERED TRACES ===")
#     # filtered_traces = [
#     #     trace
#     #     for trace in energy_projections_fig.data
#     #     if any(citation in trace.name for citation in filtered_df["citation"].unique())
#     # ]
#     # print(f"Filtered traces: {len(filtered_traces)}")
#     # for i, trace in enumerate(filtered_traces):
#     #     point_count = len(trace.x) if hasattr(trace, "x") and trace.x is not None else 0
#     #     print(f"  {i}: {trace.name} ({point_count} points)")
#     # print("=== END FILTERED TRACES ===\n")

#     # If filters are applied, determine which traces should be highlighted
#     if filters_applied and not filtered_df.empty:
#         # Create a set of tuples to identify which traces match the filter
#         filtered_trace_keys = set()
#         if "label" in filtered_df.columns:
#             for _, row in filtered_df.iterrows():
#                 filtered_trace_keys.add((row["citation"], row["label"]))
#         else:
#             for citation in filtered_df["citation"].unique():
#                 # If no label column, add all labels for this citation
#                 citation_labels = plot_df[plot_df["citation"] == citation][
#                     "label"
#                 ].unique()
#                 for label in citation_labels:
#                     filtered_trace_keys.add((citation, label))

#         # Update trace styling based on whether they match the filter
#         for i, trace in enumerate(energy_projections_fig.data):
#             # Extract citation and label from trace
#             trace_citation = None
#             trace_label = None

#             # Plotly assigns trace names based on the color and line_dash variables
#             # For color="citation", line_dash="label", the trace name follows pattern "citation, label"
#             if hasattr(trace, "name") and trace.name:
#                 if ", " in trace.name:
#                     trace_citation, trace_label = trace.name.split(", ", 1)
#                 else:
#                     # Fallback: try to get from customdata
#                     if (
#                         hasattr(trace, "customdata")
#                         and trace.customdata is not None
#                         and len(trace.customdata) > 0
#                     ):
#                         trace_citation = trace.customdata[0][0]
#                         trace_label_raw = trace.customdata[0][7]
#                         if trace_label_raw and trace_label_raw.startswith("Scenario: "):
#                             trace_label = trace_label_raw.replace(
#                                 "Scenario: ", ""
#                             ).replace("<br>", "")

#             # # Debug print to see what we're getting
#             # if i < 3:
#             #     print(
#             #         f"Trace {i}: name='{trace.name}', extracted citation='{trace_citation}', label='{trace_label}'"
#             #     )

#             # Check if this trace matches the filter
#             trace_key = (trace_citation, trace_label)
#             is_filtered = trace_key in filtered_trace_keys

#             # if is_filtered and i < 3:
#             #     print(
#             #         f"Trace {i}: name='{trace.name}', extracted citation='{trace_citation}', label='{trace_label}'"
#             #     )

#     # If filters are applied, determine which traces should be highlighted
#     if filters_applied and not filtered_df.empty:
#         # Create a set of tuples to identify which traces match the filter
#         filtered_trace_keys = set()
#         if "label" in filtered_df.columns:
#             for _, row in filtered_df.iterrows():
#                 filtered_trace_keys.add((row["citation"], row["label"]))
#         else:
#             for citation in filtered_df["citation"].unique():
#                 # If no label column, add all labels for this citation
#                 citation_labels = plot_df[plot_df["citation"] == citation][
#                     "label"
#                 ].unique()
#                 for label in citation_labels:
#                     filtered_trace_keys.add((citation, label))

#         # # Debug print to see what we're looking for
#         # print(f"Filtered trace keys to match: {filtered_trace_keys}")
#         # print(
#         #     f"Sample filtered data labels: {filtered_df['label'].unique() if 'label' in filtered_df.columns else 'No label column'}"
#         # )

#         # Update trace styling based on whether they match the filter
#         for i, trace in enumerate(energy_projections_fig.data):
#             # Extract citation and label from trace
#             trace_citation = None
#             trace_label = None

#             # Plotly assigns trace names based on the color and line_dash variables
#             # For color="citation", line_dash="label", the trace name follows pattern "citation, formatted_label"
#             if hasattr(trace, "name") and trace.name:
#                 if ", " in trace.name:
#                     trace_citation, trace_label_formatted = trace.name.split(", ", 1)
#                     # Clean up the label - remove "Scenario: " prefix and "<br>" suffix
#                     trace_label = trace_label_formatted.replace(
#                         "Scenario: ", ""
#                     ).replace("<br>", "")

#             # # Debug print for first few traces only to avoid spam
#             # if i < 6:
#             #     print(
#             #         f"Trace {i}: name='{trace.name}', citation='{trace_citation}', cleaned_label='{trace_label}'"
#             #     )

#             # Check if this trace matches the filter
#             trace_key = (trace_citation, trace_label)
#             is_filtered = trace_key in filtered_trace_keys

#             # if i < 6:
#             #     print(f"  -> trace_key={trace_key}, is_filtered={is_filtered}")

#             if is_filtered:
#                 # This trace matches the filter - show in color with full hover
#                 energy_projections_fig.data[i].update(
#                     marker=dict(
#                         size=6, opacity=0.7, line=dict(width=0.5, color="grey")
#                     ),
#                     line=dict(width=2),
#                     opacity=1.0,
#                     showlegend=True,
#                     hovertemplate=(
#                         "<b>Publication: %{customdata[0]}</b><br>"
#                         + "Year: %{x}<br>"
#                         + f"{y_label}: "+"%{y:.2f}<br>"
#                         + "%{customdata[3]}"
#                         + "%{customdata[4]}"
#                         + "%{customdata[5]}"
#                         + "<extra></extra>"
#                     ),
#                 )
#             else:
#                 # This trace doesn't match the filter - show in gray with minimal hover
#                 energy_projections_fig.data[i].update(
#                     line=dict(color="lightgray", width=2),
#                     opacity=0.4,
#                     marker=dict(size=5, opacity=0.6),
#                     showlegend=False,
#                     hovertemplate=(
#                         "<b>%{customdata[0]}</b><br>"
#                         + "Year: %{x}<br>"
#                         + f"{y_label}: "+"%{y:.2f}<br>"
#                         + "<extra></extra>"
#                     ),
#                 )
#     else:
#         # No filters applied - show all traces in gray
#         energy_projections_fig.update_traces(
#             line=dict(color="lightgray", width=2),
#             opacity=0.6,
#             marker=dict(size=5, opacity=0.7),
#             showlegend=False,
#             hovertemplate=(
#                 "<b>%{customdata[0]}</b><br>"
#                 + "Year: %{x}<br>"
#                 + f"{y_label}: "+"%{y:.2f}<br>"
#                 + "<extra></extra>"
#             ),
#         )

#     energy_projections_fig.update_xaxes(
#         range=[xmin, xmax],
#         showgrid=False,
#         showline=True,
#         linecolor="black",
#         linewidth=1,
#         title_font=dict(size=14),
#     )

#     energy_projections_fig.update_layout(
#         font_family="Inter",
#         plot_bgcolor="white",
#         margin=dict(r=250),
#         xaxis=dict(
#             showgrid=False,  # disable gridlines
#             dtick=1,  # force yearly intervals
#             showline=True,
#             linecolor="black",
#             linewidth=1,
#             title_font=dict(size=14),
#         ),
#         yaxis=dict(
#             range=[
#                 ymin,
#                 ymax,
#             ],
#             showgrid=False,  # Disable gridlines
#             showline=True,
#             linecolor="black",
#             linewidth=1,
#             title_font=dict(size=14),
#         ),
#         legend=dict(
#             orientation="v",
#             yanchor="top",
#             y=1,
#             xanchor="left",
#             x=1.02,
#             traceorder="normal",
#         ),
#         showlegend=filters_applied,
#         template="simple_white",
#     )

#     # Apply line dash styles
#     for trace in energy_projections_fig.data:
#         # Extract label from custom data if available
#         if (
#             hasattr(trace, "customdata")
#             and trace.customdata is not None
#             and len(trace.customdata) > 0
#         ):
#             label = trace.customdata[0][7]  # label is 8th custom data field
#             if label and label.startswith("Scenario: "):
#                 clean_label = label.replace("Scenario: ", "").replace("<br>", "")
#                 if clean_label in line_style_map:
#                     trace.line["dash"] = line_style_map[clean_label]

#     # # DEBUG: Final filtered traces
#     # print(f"\n=== FINAL FILTERED TRACES ===")
#     # final_filtered_traces = [
#     #     trace
#     #     for trace in energy_projections_fig.data
#     #     if any(citation in trace.name for citation in filtered_df["citation"].unique())
#     # ]
#     # print(f"Final filtered traces: {len(final_filtered_traces)}")
#     # for i, trace in enumerate(final_filtered_traces):
#     #     print(f"  {i}: {trace.name}")
#     # print("=== END FINAL FILTERED TRACES ===\n")

#     return energy_projections_fig

# ### GO ####
# import plotly.express as px
# import plotly.graph_objects as go
# import pandas as pd


# def create_energy_projections_line_plot(
#     filtered_df,
#     full_df=None,
#     filters_applied=False,
#     yaxis_title="Energy Demand (TWh)",
#     y_label="Energy Demand (TWh)"
# ):
#     """
#     Create Energy projections line plot with dual legend system

#     Args:
#         filtered_df: DataFrame to display
#         filters_applied: Boolean indicating if filters are actively applied
#         full_df: unfiltered DataFrame
#     """

#     # Sort by company name for consistent ordering
#     full_df = full_df.sort_values(["citation", "year"]).copy()
#     filtered_df = filtered_df.sort_values(["citation", "year"]).copy()

#     # Calculate y-axis range to avoid extra empty space
#     ymin = full_df["energy_demand"].min() - 10
#     ymax = full_df["energy_demand"].max() + 10

#     # Calculate x-axis range to avoid extra empty space
#     xmin = full_df["year"].min() - 1
#     xmax = full_df["year"].max() + 1

#     if full_df.empty:
#         return {
#             "data": [],
#             "layout": {
#                 "xaxis": {"title": "Year", "visible": True},
#                 "yaxis": {"title": yaxis_title, "visible": True},
#                 "showlegend": False,
#                 "annotations": [
#                     {
#                         "text": "No data available for selected filters",
#                         "xref": "paper",
#                         "yref": "paper",
#                         "x": 0.5,
#                         "y": 0.5,
#                         "showarrow": False,
#                         "font": {"size": 16, "color": "gray"},
#                     }
#                 ],
#                 "plot_bgcolor": "white",
#             },
#         }

#     # Create fields for hover text
#     def create_hover_text(df):
#         """Process DataFrame fields for hover text display"""
#         df["region"] = df["region"].apply(
#             lambda x: f"Study Region: {x}<br>" if pd.notna(x) and str(x).strip() else ""
#         )
#         df["data_center_type_s_"] = df["data_center_type_s_"].apply(
#             lambda x: f"Data Center Type(s): {x}<br>"
#             if pd.notna(x) and str(x).strip()
#             else ""
#         )
#         df["modeling_approach_es_"] = df["modeling_approach_es_"].apply(
#             lambda x: f"Modeling Approach(es): {x}<br>"
#             if pd.notna(x) and str(x).strip()
#             else ""
#         )
#         df["time_horizon"] = df["time_horizon"].apply(
#             lambda x: f"Time Horizon: {x}<br>" if pd.notna(x) and str(x).strip() else ""
#         )
#         df["label"] = df["label"].apply(
#             lambda x: f"Scenario: {x}<br>" if pd.notna(x) and str(x).strip() else ""
#         )

#     custom_data = [
#         "citation",
#         "energy_demand",
#         "year",
#         "region",
#         "data_center_type_s_",
#         "modeling_approach_es_",
#         "time_horizon",
#         "label",
#     ]

#     # Always work with the full dataset
#     plot_df = full_df.copy()
#     create_hover_text(plot_df)

#     # Define line styles for different labels
#     line_style_map = {
#         "Historical": "solid",
#         "Lower scenario": "dash", 
#         "Upper scenario": "dot",
#     }

#     # Get citations and create color mapping
#     citations = filtered_df["citation"].unique() if filters_applied else full_df["citation"].unique()
#     palette = px.colors.qualitative.Dark24
#     color_map = {
#         citation: palette[i % len(palette)] for i, citation in enumerate(citations)
#     }

#     # Create figure manually using go.Figure for better legend control
#     fig = go.Figure()
    
#     # Track which combinations we've added to avoid duplicates
#     added_combinations = set()
    
#     # If filters are applied, determine which traces should be highlighted
#     filtered_trace_keys = set()
#     if filters_applied and not filtered_df.empty:
#         if "label" in filtered_df.columns:
#             for _, row in filtered_df.iterrows():
#                 filtered_trace_keys.add((row["citation"], row["label"]))
#         else:
#             for citation in filtered_df["citation"].unique():
#                 citation_labels = plot_df[plot_df["citation"] == citation]["label"].unique()
#                 for label in citation_labels:
#                     filtered_trace_keys.add((citation, label))

#     # Add data traces (these will not show in legend)
#     for citation in plot_df["citation"].unique():
#         citation_data = plot_df[plot_df["citation"] == citation]
        
#         for label in citation_data["label"].unique():
#             if label and not pd.isna(label):
#                 label_clean = label.replace("Scenario: ", "").replace("<br>", "")
#                 combination_key = (citation, label_clean)
                
#                 if combination_key in added_combinations:
#                     continue
#                 added_combinations.add(combination_key)
                
#                 # Get data for this specific citation-label combination
#                 trace_data = citation_data[citation_data["label"] == label]
                
#                 # Determine if this trace should be highlighted
#                 if filters_applied:
#                     is_filtered = (citation, label_clean) in filtered_trace_keys
#                 else:
#                     is_filtered = False  # No filters applied - show all traces in gray
                
#                 # Set trace styling based on filter status
#                 if is_filtered:
#                     line_color = color_map.get(citation, "blue")
#                     line_width = 2.5
#                     opacity = 1.0
#                     marker_size = 6
#                     marker_opacity = 0.7
#                     hover_template = (
#                         "<b>Publication: %{customdata[0]}</b><br>"
#                         + "Year: %{x}<br>"
#                         + f"{y_label}: " + "%{y:.2f}<br>"
#                         + "%{customdata[3]}"
#                         + "%{customdata[4]}"
#                         + "%{customdata[5]}"
#                         + "<extra></extra>"
#                     )
#                 else:
#                     line_color = "lightgray"
#                     line_width = 1.8
#                     opacity = 0.45
#                     marker_size = 5
#                     marker_opacity = 0.6
#                     hover_template = (
#                         "<b>%{customdata[0]}</b><br>"
#                         + "Year: %{x}<br>"
#                         + f"{y_label}: " + "%{y:.2f}<br>"
#                         + "<extra></extra>"
#                     )
                
#                 # Get line dash style
#                 dash_style = line_style_map.get(label_clean, "solid")
                
#                 fig.add_trace(go.Scatter(
#                     x=trace_data["year"],
#                     y=trace_data["energy_demand"],
#                     mode='lines+markers',
#                     line=dict(
#                         color=line_color,
#                         width=line_width,
#                         dash=dash_style
#                     ),
#                     marker=dict(
#                         size=marker_size,
#                         opacity=marker_opacity,
#                         line=dict(width=0.5, color="grey") if is_filtered else dict(width=0)
#                     ),
#                     opacity=opacity,
#                     customdata=trace_data[custom_data].values,
#                     hovertemplate=hover_template,
#                     showlegend=False,  # Hide from legend - we'll add custom legend entries
#                     name=f"{citation} - {label_clean}"
#                 ))

#     # Add custom legend entries for scenarios (only if filters are applied)
#     if filters_applied and filtered_df is not None and not filtered_df.empty:
#         # Get unique labels from filtered data
#         if "label" in filtered_df.columns:
#             unique_labels = filtered_df["label"].unique()
#         else:
#             unique_labels = plot_df["label"].unique()
        
#         scenario_colors = ["black", "black", "black"]  # Use black for scenario legend
        
#         # Add scenario legend entries
#         for i, label in enumerate(sorted(unique_labels)):
#             if label and not pd.isna(label):
#                 label_clean = label.replace("Scenario: ", "").replace("<br>", "")
#                 dash_style = line_style_map.get(label_clean, "solid")
                
#                 fig.add_trace(go.Scatter(
#                     x=[None], y=[None],  # Empty trace just for legend
#                     mode='lines',
#                     line=dict(
#                         color=scenario_colors[i % len(scenario_colors)],
#                         width=2,
#                         dash=dash_style
#                     ),
#                     name=label_clean,
#                     showlegend=True,
#                     legendgroup="scenarios",
#                     hovertemplate="<extra></extra>",  # Hide hover
#                 ))
        
#         # Add separator (invisible trace with blank name)
#         fig.add_trace(go.Scatter(
#             x=[None], y=[None],
#             mode='lines',
#             line=dict(color="rgba(0,0,0,0)", width=0),
#             name="",  # Empty name creates visual separation
#             showlegend=True,
#             legendgroup="separator",
#             hovertemplate="<extra></extra>",
#         ))
        
#         # Add citation legend entries
#         for citation in sorted(citations):
#             fig.add_trace(go.Scatter(
#                 x=[None], y=[None],  # Empty trace just for legend
#                 mode='lines',
#                 line=dict(
#                     color=color_map.get(citation, "blue"),
#                     width=2
#                 ),
#                 name=citation,
#                 showlegend=True,
#                 legendgroup="citations",
#                 hovertemplate="<extra></extra>",  # Hide hover
#             ))

#     fig.update_xaxes(
#         range=[xmin, xmax],
#         showgrid=False,
#         showline=True,
#         linecolor="black",
#         linewidth=1,
#         title_font=dict(size=14),
#     )

#     fig.update_layout(
#         font_family="Inter",
#         plot_bgcolor="white",
#         margin=dict(r=300),  # Increased right margin for legend
#         xaxis=dict(
#             showgrid=False,  # disable gridlines
#             dtick=1,  # force yearly intervals
#             showline=True,
#             linecolor="black",
#             linewidth=1,
#             title_font=dict(size=14),
#         ),
#         yaxis=dict(
#             range=[
#                 ymin,
#                 ymax,
#             ],
#             showgrid=False,  # Disable gridlines
#             showline=True,
#             linecolor="black",
#             linewidth=1,
#             title_font=dict(size=14),
#         ),
#         legend=dict(
#             orientation="v",
#             yanchor="top",
#             y=1,
#             xanchor="left",
#             x=1.02,
#             traceorder="normal",
#         ),
#         showlegend=filters_applied,
#         template="simple_white",
#     )

#     return fig

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def create_energy_projections_line_plot(
    filtered_df,
    full_df=None,
    filters_applied=False,
    yaxis_title="Energy Demand (TWh)",
    y_label="Energy Demand (TWh)"
):
    """
    Create Energy projections line plot with dual legend system

    Args:
        filtered_df: DataFrame to display
        filters_applied: Boolean indicating if filters are actively applied
        full_df: unfiltered DataFrame
    """

    # Sort by company name for consistent ordering
    full_df = full_df.sort_values(["citation", "year"]).copy()
    filtered_df = filtered_df.sort_values(["citation", "year"]).copy()

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
                "xaxis": {"title": "Year", "visible": True},
                "yaxis": {"title": yaxis_title, "visible": True},
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

    # Always work with the full dataset
    plot_df = full_df.copy()
    create_hover_text(plot_df)

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

    # Create the line plot with the full dataset (PRESERVE ORIGINAL LOGIC)
    energy_projections_fig = px.line(
        plot_df,
        x="year",
        y="energy_demand",
        color="citation",
        line_dash="label",
        markers=True,
        labels={
            "year": "Year",
            "energy_demand": y_label,
            "citation": "Study",
            "label": "Scenario",
        },
        color_discrete_map=color_map,
        custom_data=custom_data,
        template="simple_white",
    )

    # If filters are applied, determine which traces should be highlighted (PRESERVE ORIGINAL LOGIC)
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

        # Update trace styling based on whether they match the filter (PRESERVE ORIGINAL LOGIC)
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

            # Check if this trace matches the filter
            trace_key = (trace_citation, trace_label)
            is_filtered = trace_key in filtered_trace_keys

            if is_filtered:
                # This trace matches the filter - show in color with full hover
                energy_projections_fig.data[i].update(
                    marker=dict(
                        size=6, opacity=0.7, line=dict(width=0.5, color="grey")
                    ),
                    line=dict(width=2),
                    opacity=1.0,
                    showlegend=False,  # Hide original legend entries for dual legend
                    hovertemplate=(
                        "<b>Publication: %{customdata[0]}</b><br>"
                        + "Year: %{x}<br>"
                        + f"{y_label}: "+"%{y:.2f}<br>"
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
                    marker=dict(size=5, opacity=0.6),
                    showlegend=False,  # Hide original legend entries for dual legend
                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>"
                        + "Year: %{x}<br>"
                        + f"{y_label}: "+"%{y:.2f}<br>"
                        + "<extra></extra>"
                    ),
                )
    else:
        # No filters applied - show all traces in gray (PRESERVE ORIGINAL LOGIC)
        energy_projections_fig.update_traces(
            line=dict(color="lightgray", width=2),
            opacity=0.6,
            marker=dict(size=5, opacity=0.7),
            showlegend=False,  # Hide original legend entries for dual legend
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                + "Year: %{x}<br>"
                + f"{y_label}: "+"%{y:.2f}<br>"
                + "<extra></extra>"
            ),
        )

    # Apply line dash styles (PRESERVE ORIGINAL LOGIC)
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

    # ADD DUAL LEGEND SYSTEM (only if filters are applied)
    if filters_applied and filtered_df is not None and not filtered_df.empty:
        # Get unique labels from filtered data
        if "label" in filtered_df.columns:
            unique_labels = filtered_df["label"].unique()
        else:
            unique_labels = plot_df["label"].unique()
        
        scenario_colors = ["black", "black", "black"]  # Use black for scenario legend
        
        # Add scenario legend entries
        for i, label in enumerate(sorted(unique_labels)):
            if label and not pd.isna(label):
                label_clean = label.replace("Scenario: ", "").replace("<br>", "")
                dash_style = line_style_map.get(label_clean, "solid")
                
                energy_projections_fig.add_trace(go.Scatter(
                    x=[None], y=[None],  # Empty trace just for legend
                    mode='lines',
                    line=dict(
                        color=scenario_colors[i % len(scenario_colors)],
                        width=2,
                        dash=dash_style
                    ),
                    name=label_clean,
                    showlegend=True,
                    legendgroup="scenarios",
                    hovertemplate="<extra></extra>",  # Hide hover
                ))
        
        # Add separator (invisible trace with blank name)
        energy_projections_fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='lines',
            line=dict(color="rgba(0,0,0,0)", width=0),
            name="",  # Empty name creates visual separation
            showlegend=True,
            legendgroup="separator",
            hovertemplate="<extra></extra>",
        ))
        
        # Add citation legend entries
        for citation in sorted(citations):
            energy_projections_fig.add_trace(go.Scatter(
                x=[None], y=[None],  # Empty trace just for legend
                mode='lines',
                line=dict(
                    color=color_map.get(citation, "blue"),
                    width=2
                ),
                name=citation,
                showlegend=True,
                legendgroup="citations",
                hovertemplate="<extra></extra>",  # Hide hover
            ))

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
        margin=dict(r=300),  # Increased right margin for dual legend
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
            title_text="",
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.05,
            traceorder="normal",
        ),
        showlegend=filters_applied,
        template="simple_white",
    )

    return energy_projections_fig