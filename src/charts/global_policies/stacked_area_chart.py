import plotly.express as px
import plotly.io as pio
import pandas as pd
import colorsys
import plotly.colors as pc


def create_global_policies_stacked_area_plot(filtered_df, full_df=None, filters_applied=False):
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
    #full_df = full_df.copy()

    filtered_df["area_group"] = filtered_df["country"] + " - " + filtered_df["jurisdiction_level"]
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

    # Ensure all years are present for each area_group (fill missing years with 0)
    # This is important for correct cumulative calculation
    all_years = sorted(df_yearly["year_introduced"].unique())
    all_area_groups = df_yearly["area_group"].unique()

    # Create complete year-area_group combinations
    from itertools import product

    complete_index = pd.DataFrame(
        list(product(all_years, all_area_groups)), columns=["year_introduced", "area_group"]
    )

    # Merge with actual data, filling missing with 0
    df_yearly = complete_index.merge(
        df_yearly, on=["year_introduced", "area_group"], how="left"
    ).fillna({"unique_ids": 0})

    # Sort FIRST by area_group and year_introduced (important for cumulative calculation)
    df_yearly = df_yearly.sort_values(["area_group", "year_introduced"])

    # Calculate cumulative sum AFTER sorting (so it accumulates correctly across years)
    df_yearly["cumulative_policues"] = df_yearly.groupby("area_group")[
        "unique_ids"
    ].cumsum()

    # Get final cumulative count for each area_group (for legend sorting and labels)
    final_counts = (
        df_yearly.groupby("area_group")["cumulative_policues"].max().reset_index()
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
    fig = px.area(
        df_yearly,
        x="year_introduced",
        y="cumulative_policues",
        color="area_group_label",
        line_group="area_group_label",
        color_discrete_map=color_map_labeled,
        template="plotly_white",
        # facet_col="jurisdiction_level",  # optional — separate panels for national/city
        title="Cumulative Number of Policies Over Time",
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

    return fig