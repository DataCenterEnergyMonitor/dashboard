import plotly.express as px
import plotly.io as pio
import pandas as pd
import colorsys
import plotly.colors as pc
from datetime import datetime


def create_gp_stacked_area_plot(
    filtered_df, full_df=None, filters_applied=False
):
    """
    Create stacked area plot

    Args:
        filtered_df: DataFrame to display
        filters_applied: Boolean indicating if filters are actively applied
        full_df: unfiltered DataFrame
    """

    # Reset template to avoid Plotly template corruption bug
    pio.templates.default = "simple_white"

    # Make copies to avoid modifying the original DataFrames
    filtered_df = filtered_df.copy()
    # full_df = full_df.copy()

    filtered_df["area_group"] = (
        filtered_df["country"] + " - " + filtered_df["jurisdiction_level"]
    )
    df_unique = filtered_df.drop_duplicates(
        subset=[
            "policy_id",
            "area_group",
            "authors",
            "jurisdiction_level",
            "region",
            "supranational_policy_area",
            "country",
            "state_province",
            "city",
            "county",
            "order_type",
            "status",
            "year_introduced",
        ]
    )

    # Count unique policies per year and area_group
    df_yearly = (
        df_unique.groupby(["year_introduced", "area_group"])["policy_id"]
        .nunique()
        .reset_index(name="unique_ids")
    )

    # Remove rows with NaN year_introduced for cleaner plot
    df_yearly = df_yearly[df_yearly["year_introduced"].notna()]

    # Convert year_introduced to numeric and then to int to ensure consistent type
    df_yearly["year_introduced"] = pd.to_numeric(
        df_yearly["year_introduced"], errors="coerce"
    )
    df_yearly = df_yearly[df_yearly["year_introduced"].notna()]
    df_yearly["year_introduced"] = df_yearly["year_introduced"].astype(int)

    # Ensure all years are present for each area_group (fill missing years with 0)
    # This is important for correct cumulative calculation
    all_years = sorted(df_yearly["year_introduced"].unique())
    # Ensure all_years are integers
    all_years = [int(year) for year in all_years]
    all_area_groups = df_yearly["area_group"].unique()

    # Get the minimum year from the full dataset (baseline year, e.g., 2007)
    # If full_df is provided, use its min year, otherwise use 2007 as default
    if full_df is not None and "year_introduced" in full_df.columns:
        full_df_years = pd.to_numeric(
            full_df["year_introduced"], errors="coerce"
        ).dropna()
        if len(full_df_years) > 0:
            baseline_year = int(full_df_years.min())
        else:
            baseline_year = 2007  # Default baseline year
    else:
        baseline_year = 2007  # Default baseline year

    # If there's only one year in the filtered data, add baseline year as first point (with 0 policies)
    # Area plots need at least 2 points to display
    # For single data point: baseline_year - data_year shows 0 policies, data_year onwards shows actual count
    if len(all_years) == 1:
        data_year = all_years[0]
        # Add baseline year before the data year (ensure baseline_year < data_year)
        if baseline_year >= data_year:
            baseline_year = (
                data_year - 1
            )  # Use year before data year if baseline is not earlier
        all_years = [baseline_year, data_year]
        print(
            f"Only one year found ({data_year}), adding baseline year {baseline_year} for area plot rendering"
        )

    # Create complete year-area_group combinations
    from itertools import product

    complete_index = pd.DataFrame(
        list(product(all_years, all_area_groups)),
        columns=["year_introduced", "area_group"],
    )

    # Ensure year_introduced is int type to match df_yearly
    complete_index["year_introduced"] = complete_index["year_introduced"].astype(int)

    # Merge with actual data, filling missing with 0
    df_yearly = complete_index.merge(
        df_yearly, on=["year_introduced", "area_group"], how="left"
    ).fillna({"unique_ids": 0})

    # Sort FIRST by area_group and year_introduced (important for cumulative calculation)
    df_yearly = df_yearly.sort_values(["area_group", "year_introduced"])

    # Calculate cumulative sum AFTER sorting (so it accumulates correctly across years)
    df_yearly["cumulative_policies"] = df_yearly.groupby("area_group")[
        "unique_ids"
    ].cumsum()

    # If we added a baseline year for single-year case, ensure baseline year has 0 cumulative policies
    # and extend the data year's cumulative value to current year
    original_years = sorted(
        df_yearly[df_yearly["unique_ids"] > 0]["year_introduced"].unique()
    )
    if len(original_years) == 1 and len(all_years) == 2:
        data_year = original_years[0]
        baseline_year = all_years[0]  # First year is the baseline
        current_year = datetime.now().year

        # For each area_group:
        # 1. Set baseline year cumulative to 0 (already done by merge with fillna, but ensure it)
        # 2. Add current year with same cumulative as data year (flat line after data year)
        for area_group in all_area_groups:
            # Ensure baseline year is 0
            baseline_mask = (df_yearly["area_group"] == area_group) & (
                df_yearly["year_introduced"] == baseline_year
            )
            if baseline_mask.any():
                df_yearly.loc[baseline_mask, "cumulative_policies"] = 0
                df_yearly.loc[baseline_mask, "unique_ids"] = 0

            # Add current year with same cumulative as data year (if current year > data year)
            if current_year > data_year:
                data_year_mask = (df_yearly["area_group"] == area_group) & (
                    df_yearly["year_introduced"] == data_year
                )
                if data_year_mask.any():
                    cumulative_value = df_yearly.loc[
                        data_year_mask, "cumulative_policies"
                    ].iloc[0]
                    # Check if current year already exists, if not add it
                    current_year_mask = (df_yearly["area_group"] == area_group) & (
                        df_yearly["year_introduced"] == current_year
                    )
                    if not current_year_mask.any():
                        # Add new row for current year
                        new_row = pd.DataFrame(
                            {
                                "year_introduced": [current_year],
                                "area_group": [area_group],
                                "unique_ids": [0],
                                "cumulative_policies": [cumulative_value],
                            }
                        )
                        df_yearly = pd.concat([df_yearly, new_row], ignore_index=True)
                        # Update all_years to include current_year for proper x-axis range
                        if current_year not in all_years:
                            all_years.append(current_year)
                            all_years = sorted(all_years)
                    else:
                        df_yearly.loc[current_year_mask, "cumulative_policies"] = (
                            cumulative_value
                        )
                        df_yearly.loc[current_year_mask, "unique_ids"] = 0

    # Get final cumulative count for each area_group (for legend sorting and labels)
    final_counts = (
        df_yearly.groupby("area_group")["cumulative_policies"].max().reset_index()
    )
    final_counts.columns = ["area_group", "final_count"]

    # # Diagnostic: Check which countries are in the data vs in the plot
    # unique_country = df["country"].unique()
    # countries_in_plot = df_yearly["area_group"].str.split(" - ").str[0].unique()
    # missing_countries = set(unique_country) - set(countries_in_plot)
    # print(f"Total unique countries in data: {len(unique_country)}")
    # print(f"Countries in plot: {len(countries_in_plot)}")
    # if len(missing_countries) > 0:
    #     print(
    #         f"Missing countries (no valid year_introduced data): {sorted(missing_countries)}"
    #     )

    # Create color mapping: same base color for country, different shades for jurisdiction levels
    # Get unique countries and assign base colors using Plotly palettes
    unique_countries = sorted(df_yearly["area_group"].str.split(" - ").str[0].unique())

    # Use Plotly's alphabet palette (26 distinct colors) - good for color-blind users
    # Can also use dark24 or light24 if preferred
    palette = pc.qualitative.Plotly  # 26 distinct colors
    # If we need more colors, combine with other palettes
    if len(unique_countries) > 26:
        palette = palette + pc.qualitative.Dark24 + pc.qualitative.Light24

    # Assign unique colors to each country (no repetition)
    country_colors = {}
    for i, country in enumerate(unique_countries):
        color = palette[i % len(palette)]
        country_colors[country] = color

    # Create color map for area_groups with different shades for jurisdiction levels
    def adjust_color_shade(hex_color, shade_factor):
        """Adjust color shade: shade_factor > 1 = lighter, < 1 = darker
        Expects hex color format"""
        # Convert hex to RGB
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

        # Convert to HSV, adjust brightness, convert back
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        v = min(1.0, v * shade_factor)  # Adjust brightness
        r, g, b = colorsys.hsv_to_rgb(h, s, v)

        # Convert back to hex
        return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"

    # Merge final counts with area_groups and create labels with counts
    df_yearly = df_yearly.merge(final_counts, on="area_group", how="left")

    # Create new labels with counts: "Country - Jurisdiction (count)"
    df_yearly["area_group_label"] = (
        df_yearly["area_group"]
        + " ("
        + df_yearly["final_count"].astype(int).astype(str)
        + ")"
    )

    # Sort area_groups by final count (descending) for legend order
    area_groups_sorted = final_counts.sort_values("final_count", ascending=False)[
        "area_group"
    ].tolist()

    # Get unique area_groups and assign colors
    color_map = {}
    jurisdiction_shades = {
        "Country": 1.0,  # Full brightness
        "State": 0.85,  # Slightly darker (brighter than before)
        "City": 0.7,  # Medium shade (brighter than before)
        "County": 0.55,  # Darker but still visible (brighter than before)
        "Local": 0.75,  # Medium-bright shade
        "Multi-National": 0.9,  # Very slightly darker
    }

    for area_group in area_groups_sorted:
        country = area_group.split(" - ")[0]
        jurisdiction = area_group.split(" - ")[1] if " - " in area_group else "Country"

        base_color = country_colors[country]
        shade_factor = jurisdiction_shades.get(jurisdiction, 0.7)  # Default shade
        color_map[area_group] = adjust_color_shade(base_color, shade_factor)

    # Create mapping from original area_group to labeled version for color_discrete_map
    # We need to map the new labels to colors
    color_map_labeled = {}
    for area_group in area_groups_sorted:
        final_count = final_counts[final_counts["area_group"] == area_group][
            "final_count"
        ].iloc[0]
        labeled_name = f"{area_group} ({int(final_count)})"
        color_map_labeled[labeled_name] = color_map[area_group]

    # Create figure with labeled area_groups
    # Add unique_ids as custom_data so we can show policies introduced per year in hover
    fig = px.area(
        df_yearly,
        x="year_introduced",
        y="cumulative_policies",
        color="area_group_label",
        line_group="area_group_label",
        color_discrete_map=color_map_labeled,
        custom_data=["unique_ids"],  # Add unique_ids for hover display
        template="plotly_white",
        labels={
            "cumulative_policies": "Number of Policies",
            "year_introduced": "Year Introduced",
            "area_group_label": "Geographic Scope - Jurisdiction Level (Policy Count)"
        },
        # facet_col="jurisdiction_level",  # optional — separate panels for national/city
        # title="Cumulative Number of Policies Over Time",
    )

    # Update hover template with user-friendly names
    # Show: Area Group, Year, Policies Introduced (in that year), Cumulative Policies
    fig.update_traces(
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            + "Year: %{x}<br>"
            + "Policies Introduced: %{customdata[0]}<br>"
            + "Cumulative Policies: %{y}<br>"
            + "<extra></extra>"
        )
    )

    # Sort legend by final count (descending) - update trace order
    # Get the order based on final counts
    legend_order = []
    for area_group in area_groups_sorted:
        final_count = final_counts[final_counts["area_group"] == area_group][
            "final_count"
        ].iloc[0]
        labeled_name = f"{area_group} ({int(final_count)})"
        legend_order.append(labeled_name)

    # Reorder traces to match legend order
    fig.data = sorted(
        fig.data,
        key=lambda x: legend_order.index(x.name)
        if x.name in legend_order
        else len(legend_order),
    )

    # Adjust x-axis to start from min year - 1 for better readability
    min_year = df_yearly["year_introduced"].min()
    max_year = df_yearly["year_introduced"].max()
    fig.update_xaxes(range=[min_year - 1, max_year + 0.5])

    # Calculate y-axis limits based on full dataset
    # Get max cumulative policies from filtered data (sum across all groups per year, then max)
    # For each year, sum cumulative policies across all area_groups
    yearly_totals_filtered = df_yearly.groupby("year_introduced")[
        "cumulative_policies"
    ].sum()
    max_cumulative_filtered = yearly_totals_filtered.max()

    # Calculate total cumulative policies from full dataset (N)
    # This should be the sum across ALL groups, not max per group
    if full_df is not None:
        # Process full_df similar to filtered_df to get cumulative policies
        full_df_copy = full_df.copy()
        full_df_copy["area_group"] = (
            full_df_copy["country"] + " - " + full_df_copy["jurisdiction_level"]
        )
        full_df_unique = full_df_copy.drop_duplicates(
            subset=[
                "policy_id",
                "area_group",
                "authors",
                "jurisdiction_level",
                "region",
                "supranational_policy_area",
                "country",
                "state_province",
                "city",
                "county",
                "order_type",
                "status",
                "year_introduced",
            ]
        )

        # Count unique policies per year and area_group
        full_df_yearly = (
            full_df_unique.groupby(["year_introduced", "area_group"])["policy_id"]
            .nunique()
            .reset_index(name="unique_ids")
        )

        # Remove NaN years
        full_df_yearly = full_df_yearly[full_df_yearly["year_introduced"].notna()]

        # Convert year_introduced to numeric and then to int to ensure consistent type
        full_df_yearly["year_introduced"] = pd.to_numeric(
            full_df_yearly["year_introduced"], errors="coerce"
        )
        full_df_yearly = full_df_yearly[full_df_yearly["year_introduced"].notna()]
        full_df_yearly["year_introduced"] = full_df_yearly["year_introduced"].astype(
            int
        )

        if len(full_df_yearly) > 0:
            # Get all years and area groups
            full_all_years = sorted(full_df_yearly["year_introduced"].unique())
            # Ensure full_all_years are integers
            full_all_years = [int(year) for year in full_all_years]
            full_all_area_groups = full_df_yearly["area_group"].unique()

            # Create complete index
            from itertools import product

            full_complete_index = pd.DataFrame(
                list(product(full_all_years, full_all_area_groups)),
                columns=["year_introduced", "area_group"],
            )

            # Ensure year_introduced is int type
            full_complete_index["year_introduced"] = full_complete_index[
                "year_introduced"
            ].astype(int)

            # Merge and calculate cumulative
            full_df_yearly = full_complete_index.merge(
                full_df_yearly, on=["year_introduced", "area_group"], how="left"
            ).fillna({"unique_ids": 0})

            full_df_yearly = full_df_yearly.sort_values(
                ["area_group", "year_introduced"]
            )
            full_df_yearly["cumulative_policies"] = full_df_yearly.groupby(
                "area_group"
            )["unique_ids"].cumsum()

            # Calculate total cumulative across ALL groups for each year
            # Then take the max across all years
            yearly_totals_full = full_df_yearly.groupby("year_introduced")[
                "cumulative_policies"
            ].sum()
            N_cumulative_full = int(yearly_totals_full.max())
        else:
            # If full_df has no valid data, use filtered max
            N_cumulative_full = int(max_cumulative_filtered)
    else:
        # If no full_df provided, use filtered max
        N_cumulative_full = int(max_cumulative_filtered)

    # Calculate y-axis max based on the logic:
    # If filtered max < (N/5 rounded), then y_max = (N/3 rounded), else y_max = N
    threshold = round(N_cumulative_full / 5)
    if max_cumulative_filtered < threshold:
        y_max = round(N_cumulative_full / 3)
    else:
        y_max = N_cumulative_full

    # Ensure y_max is at least max_cumulative_filtered to show all data
    y_max = max(int(y_max), int(max_cumulative_filtered))

    # Set y-axis range with no decimals
    fig.update_yaxes(
        range=[0, y_max],
        tickformat="d",  # Format as integer (no decimals)
    )

    return fig
