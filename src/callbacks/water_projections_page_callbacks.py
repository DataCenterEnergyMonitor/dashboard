import dash
from pathlib import Path
from dash import Dash, Input, Output, State, callback, dcc, html, callback_context
import pandas as pd
from charts.water_projections_chart import create_water_projections_line_plot
from components.excel_export import create_filtered_excel_download
from pages.water_projections_page import create_chart_row

WATER_PROJECTION_OUTPUT_FILTERS = [
    "wp_citation",
    "wp_year_of_publication",
    "wp_publisher_institution_type_s_",
    "wp_author_institution_type_s_",
    "wp_study_region",
    "wp_data_center_type_s_",
    "wp_associated_granularity",
    "wp_modeling_approach_es_",
    "wp_input_data_type_s_",
    "wp_time_horizon",
    "wp_projection_narrative_s_",
    "wp_label",
]

# All filters including those without options (for State/Input callbacks)
WATER_PROJECTION_INPUT_FILTERS = WATER_PROJECTION_OUTPUT_FILTERS + [
    "wp_total_quality_rating",
    "wp_units",
    # Checkbox filters (for State callbacks only)
    "wp_peer_review",
    "wp_model_availability",
    "wp_data_availability",
    "wp_uncertainty_quantification",
    "wp_sensitivity_analysis",
    "wp_analytical_rigor",
    "wp_results_validation",
    "wp_granularity",
    "wp_completeness",
    "wp_technology_correlation",
    "wp_geographical_correlation",
    "wp_temporal_correlation",
]

WATER_PROJECTION_DROPDOWN_FILTERS = [
    "wp_citation",
    "wp_year_of_publication",
    "wp_publisher_institution_type_s_",
    "wp_author_institution_type_s_",
    "wp_study_region",
    "wp_data_center_type_s_",
    "wp_associated_granularity",
    "wp_modeling_approach_es_",
    "wp_input_data_type_s_",
    "wp_time_horizon",
    "wp_projection_narrative_s_",
    "wp_label",
]

WATER_PROJECTION_CHECKLIST_FILTERS = [
    "wp_peer_review",
    "wp_model_availability",
    "wp_data_availability",
    "wp_uncertainty_quantification",
    "wp_sensitivity_analysis",
    "wp_analytical_rigor",
    "wp_results_validation",
    "wp_granularity",
    "wp_completeness",
    "wp_technology_correlation",
    "wp_geographical_correlation",
    "wp_temporal_correlation",
]


def get_single_value_options(df, column):
    """For fields that should NOT be split on commas"""
    unique_values = df[column].dropna().unique()
    return [
        {"label": val, "value": val}
        for val in sorted(unique_values)
        if val and str(val).strip()
    ]


def get_multi_value_options(df, column):
    """Extract unique values from multi-value fields"""
    all_values = set()
    for value_str in df[column].dropna().unique():
        values = [v.strip() for v in str(value_str).split(",")]
        all_values.update(values)
    return [{"label": val, "value": val} for val in sorted(all_values) if val]


def merge_option_lists(list1, list2):
    """Merge two option lists, removing duplicates"""
    seen_values = set()
    merged = []

    for options_list in [list1, list2]:
        for option in options_list:
            if option["value"] not in seen_values:
                merged.append(option)
                seen_values.add(option["value"])

    return sorted(merged, key=lambda x: x["label"])


def preserve_valid_selections(current_selections, new_available_options):
    """Keep current selections that are still valid, mark invalid ones"""
    if not current_selections:
        return new_available_options

    available_values = {opt["value"] for opt in new_available_options}

    # Add back selections that are no longer available (but keep them selected)
    for selected_val in current_selections:
        if selected_val not in available_values:
            new_available_options.append(
                {
                    "label": f"{selected_val} (from previous selection)",
                    "value": selected_val,
                    "disabled": False,  # Keep it selectable so user can remove it
                }
            )

    return new_available_options


def apply_multi_value_filter(df, column, selected_values):
    """Helper function to apply multi-value string matching filter"""
    if not selected_values:
        return df

    mask = pd.Series([False] * len(df), index=df.index)
    for value in selected_values:
        mask = mask | df[column].str.contains(value, case=False, na=False, regex=False)
    return df[mask]


def apply_checkbox_filter(df, column, selected_values):
    """Helper function to apply checkbox filter with string conversion"""
    if not selected_values:
        return df
    # Convert both filter values and data to strings for comparison
    selected_values_str = [str(x) for x in selected_values]
    return df[df[column].astype(str).isin(selected_values_str)]


def get_checkbox_options_with_disabled(full_df, filtered_df, column):
    """Get checkbox options with disabled state for items not in filtered data"""

    # Get all possible values from full dataset (single values, no comma splitting)
    all_values = set(full_df[column].dropna().unique())

    # Get available values from filtered dataset (single values, no comma splitting)
    available_values = set(filtered_df[column].dropna().unique())

    # Create options with disabled state
    options = []
    for val in sorted(all_values):
        if val and str(val).strip():  # Make sure it's not empty
            options.append(
                {
                    "label": str(val),
                    "value": str(val),
                    "disabled": val
                    not in available_values,  # Grey out if not available
                }
            )
    return options


def filter_data(df, **filter_kwargs):
    """Filter dataframe based on all selections"""
    print(f"Starting with {len(df)} records")
    filtered_df = df.copy()

    # Apply units filter first
    units = filter_kwargs.get("wp_units")
    if units:
        filtered_df = filtered_df[filtered_df["units"] == units]
        print(f"After units filter: {len(filtered_df)} records")
    # Extract single-value filters
    citation, year_of_publication, time_horizon, label = [
        filter_kwargs.get(key)
        for key in [
            "wp_citation",
            "wp_year_of_publication",
            "wp_time_horizon",
            "wp_label",
        ]
    ]

    # Extract checkbox filters
    (
        peer_review,
        model_availability,
        data_availability,
        uncertainty_quantification,
        sensitivity_analysis,
        analytical_rigor,
        results_validation,
        granularity,
        completeness,
        technology_correlation,
        geographical_correlation,
        temporal_correlation,
    ) = [
        filter_kwargs.get(key)
        for key in [
            "wp_peer_review",
            "wp_model_availability",
            "wp_data_availability",
            "wp_uncertainty_quantification",
            "wp_sensitivity_analysis",
            "wp_analytical_rigor",
            "wp_results_validation",
            "wp_granularity",
            "wp_completeness",
            "wp_technology_correlation",
            "wp_geographical_correlation",
            "wp_temporal_correlation",
        ]
    ]

    # Extract multi-value filters
    (
        wp_study_region,
        publisher_institution_type_s_,
        author_institution_type_s_,
        data_center_type_s_,
        modeling_approach_es_,
        input_data_type_s_,
        projection_narrative_s_,
        associated_granularity,
    ) = [
        filter_kwargs.get(key)
        for key in [
            "wp_study_region",
            "wp_publisher_institution_type_s_",
            "wp_author_institution_type_s_",
            "wp_data_center_type_s_",
            "wp_modeling_approach_es_",
            "wp_input_data_type_s_",
            "wp_projection_narrative_s_",
            "wp_associated_granularity",
        ]
    ]

    total_quality_rating = filter_kwargs.get("wp_total_quality_rating")

    # Apply single-value filters
    if citation:
        filtered_df = filtered_df[filtered_df["citation"].isin(citation)]
    if year_of_publication:
        filtered_df = filtered_df[
            filtered_df["year_of_publication"].isin(year_of_publication)
        ]
    # associated_granularity is handled as multi-value filter below
    if time_horizon:
        filtered_df = filtered_df[filtered_df["time_horizon"].isin(time_horizon)]
    if label:
        filtered_df = filtered_df[filtered_df["label"].isin(label)]

    # Apply checkbox filters
    if peer_review:
        print(
            f"Applying peer_review filter: {peer_review} (types: {[type(x) for x in peer_review]})"
        )
        print(
            f"Sample peer_review data: {filtered_df['peer_review'].dropna().unique()[:5]} (dtype: {filtered_df['peer_review'].dtype})"
        )
        filtered_df = apply_checkbox_filter(filtered_df, "peer_review", peer_review)
        print(f"After peer_review filter: {len(filtered_df)} records")
    if model_availability:
        print(
            f"Applying model_availability filter: {model_availability} (types: {[type(x) for x in model_availability]})"
        )
        print(
            f"Sample model_availability data: {filtered_df['model_availability'].dropna().unique()[:5]} (dtype: {filtered_df['model_availability'].dtype})"
        )
        filtered_df = apply_checkbox_filter(
            filtered_df, "model_availability", model_availability
        )
        print(f"After model_availability filter: {len(filtered_df)} records")
    if data_availability:
        filtered_df = apply_checkbox_filter(
            filtered_df, "data_availability", data_availability
        )
    if uncertainty_quantification:
        filtered_df = apply_checkbox_filter(
            filtered_df, "uncertainty_quantification", uncertainty_quantification
        )
    if sensitivity_analysis:
        filtered_df = apply_checkbox_filter(
            filtered_df, "sensitivity_analysis", sensitivity_analysis
        )
    if analytical_rigor:
        filtered_df = apply_checkbox_filter(
            filtered_df, "analytical_rigor", analytical_rigor
        )
    if results_validation:
        filtered_df = apply_checkbox_filter(
            filtered_df, "results_validation", results_validation
        )
    if granularity:
        filtered_df = apply_checkbox_filter(filtered_df, "granularity", granularity)
    if completeness:
        filtered_df = apply_checkbox_filter(filtered_df, "completeness", completeness)
    if technology_correlation:
        filtered_df = apply_checkbox_filter(
            filtered_df, "technology_correlation", technology_correlation
        )
    if geographical_correlation:
        filtered_df = apply_checkbox_filter(
            filtered_df, "geographical_correlation", geographical_correlation
        )
    if temporal_correlation:
        filtered_df = apply_checkbox_filter(
            filtered_df, "temporal_correlation", temporal_correlation
        )

    # Apply range slider filter
    if total_quality_rating and len(total_quality_rating) == 2:
        min_val, max_val = total_quality_rating
        filtered_df = filtered_df[
            (filtered_df["total"] >= min_val) & (filtered_df["total"] <= max_val)
        ]

    # Apply multi-value filters
    filtered_df = apply_multi_value_filter(filtered_df, "region", wp_study_region)
    filtered_df = apply_multi_value_filter(
        filtered_df, "publisher_institution_type_s_", publisher_institution_type_s_
    )
    filtered_df = apply_multi_value_filter(
        filtered_df, "author_institution_type_s_", author_institution_type_s_
    )
    filtered_df = apply_multi_value_filter(
        filtered_df, "data_center_type_s_", data_center_type_s_
    )
    filtered_df = apply_multi_value_filter(
        filtered_df, "modeling_approach_es_", modeling_approach_es_
    )
    filtered_df = apply_multi_value_filter(
        filtered_df, "input_data_type_s_", input_data_type_s_
    )
    filtered_df = apply_multi_value_filter(
        filtered_df, "projection_narrative_s_", projection_narrative_s_
    )
    filtered_df = apply_multi_value_filter(
        filtered_df, "associated_granularity", associated_granularity
    )

    print(f"Final result: {len(filtered_df)} records")
    return filtered_df


def register_water_projections_callbacks(app, df):
    # Update filters on Apply or Clear button click
    @app.callback(
        [Output(name, "options") for name in WATER_PROJECTION_OUTPUT_FILTERS],
        [
            Input("wp-apply-filters-btn", "n_clicks"),
            Input("wp-clear-filters-btn", "n_clicks"),
            Input("wp_units", "value"),
        ],  # Only button triggers
        [
            State(name, "value") for name in WATER_PROJECTION_INPUT_FILTERS
        ],  # All filters as State
        prevent_initial_call=False,
    )
    def update_filters(apply_clicks, clear_clicks, units_value, *filter_values):
        filter_args = dict(zip(WATER_PROJECTION_INPUT_FILTERS, filter_values))
        filter_args["wp_units"] = units_value

        ctx = dash.callback_context

        if ctx.triggered:
            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

            if trigger_id == "wp-clear-filters-btn":
                print("Clear filters clicked - showing all options")
                return generate_all_options(df, units_value)

            elif trigger_id in ["wp-apply-filters-btn", "wp_units"]:
                print(f"Apply filters clicked with selections: {filter_args}")
                return generate_filtered_options(df, filter_args)
        else:
            # Initial load - show all options
            print("Initial load - showing all options")
            return generate_all_options(df, units_value)

    def generate_all_options(df, units_value):
        """Generate all available options - used on initial load and clear"""
        # Filter dataframe by units first
        units_filtered_df = df[df["units"] == units_value]

        wp_citation_opts = get_single_value_options(units_filtered_df, "citation")
        wp_pub_year_opts = get_single_value_options(
            units_filtered_df, "year_of_publication"
        )
        wp_publisher_opts = get_multi_value_options(
            units_filtered_df, "publisher_institution_type_s_"
        )
        wp_author_opts = get_multi_value_options(
            units_filtered_df, "author_institution_type_s_"
        )
        wp_study_region_opts = get_multi_value_options(units_filtered_df, "region")
        wp_data_center_type_opts = get_multi_value_options(
            units_filtered_df, "data_center_type_s_"
        )
        wp_associated_granularity_opts = get_multi_value_options(
            units_filtered_df, "associated_granularity"
        )
        wp_modeling_approach_opts = get_multi_value_options(
            units_filtered_df, "modeling_approach_es_"
        )
        wp_input_data_type_opts = get_multi_value_options(
            units_filtered_df, "input_data_type_s_"
        )
        wp_time_horizon_opts = get_single_value_options(
            units_filtered_df, "time_horizon"
        )
        wp_projection_narrative_opts = get_multi_value_options(
            units_filtered_df, "projection_narrative_s_"
        )
        wp_label_opts = get_single_value_options(units_filtered_df, "label")

        return (
            wp_citation_opts,  # 1 - citation
            wp_pub_year_opts,  # 2 - year_of_publication
            wp_publisher_opts,  # 3 - publisher_institution_type_s_
            wp_author_opts,  # 4 - author_institution_type_s_
            wp_study_region_opts,  # 17 - study_region
            wp_data_center_type_opts,  # 18 - data_center_type_s_
            wp_associated_granularity_opts,  # 19 - associated_granularity
            wp_modeling_approach_opts,  # 20 - modeling_approach_es_
            wp_input_data_type_opts,  # 21 - input_data_type_s_
            wp_time_horizon_opts,  # 22 - time_horizon
            wp_projection_narrative_opts,  # 23 - projection_narrative_s_
            wp_label_opts,  # 24 - label
        )

    @app.callback(
        [Output(name, "value") for name in WATER_PROJECTION_INPUT_FILTERS],
        [Input("wp-clear-filters-btn", "n_clicks")],
        prevent_initial_call=True,
    )
    def clear_all_filters(clear_clicks):
        if clear_clicks:
            return tuple(
                get_clear_value(name) for name in WATER_PROJECTION_INPUT_FILTERS
            )
        return dash.no_update

    def get_clear_value(filter_name):
        """Get the appropriate clear value for each filter type"""
        DROPDOWN_FILTERS = [
            "wp_citation",
            "wp_year_of_publication",
            "wp_publisher_institution_type_s_",
            "wp_author_institution_type_s_",
            "wp_study_region",
            "wp_data_center_type_s_",
            "wp_associated_granularity",
            "wp_modeling_approach_es_",
            "wp_input_data_type_s_",
            "wp_time_horizon",
            "wp_projection_narrative_s_",
            "wp_label",
        ]

        CHECKLIST_FILTERS = [
            "wp_peer_review",
            "wp_model_availability",
            "wp_data_availability",
            "wp_uncertainty_quantification",
            "wp_sensitivity_analysis",
            "wp_analytical_rigor",
            "wp_results_validation",
            "wp_granularity",
            "wp_completeness",
            "wp_technology_correlation",
            "wp_geographical_correlation",
            "wp_temporal_correlation",
        ]

        if filter_name in DROPDOWN_FILTERS:
            return None
        elif filter_name in CHECKLIST_FILTERS:
            return []
        elif filter_name == "wp_units":
            return "TWh"
        elif filter_name == "wp_total_quality_rating":
            return [12, 36]
        else:
            return None

    def generate_filtered_options(df, filter_args):
        """Generate options showing what's compatible with current selections (excluding self-filtering)"""

        print(f"Generating filtered options for selections: {filter_args}")

        # Get units value and filter the base dataframe first
        units_value = filter_args.get("wp_units")
        df = df[df["units"] == units_value]

        # Extract all current selections
        citation = filter_args.get("wp_citation")
        year_of_publication = filter_args.get("wp_year_of_publication")
        publisher_institution_type_s_ = filter_args.get(
            "wp_publisher_institution_type_s_"
        )
        author_institution_type_s_ = filter_args.get("wp_author_institution_type_s_")
        wp_study_region = filter_args.get("wp_study_region")
        data_center_type_s_ = filter_args.get("wp_data_center_type_s_")
        associated_granularity = filter_args.get("wp_associated_granularity")
        modeling_approach_es_ = filter_args.get("wp_modeling_approach_es_")
        input_data_type_s_ = filter_args.get("wp_input_data_type_s_")
        time_horizon = filter_args.get("wp_time_horizon")
        projection_narrative_s_ = filter_args.get("wp_projection_narrative_s_")
        label = filter_args.get("wp_label")
        total_quality_rating = filter_args.get("wp_total_quality_rating")

        # Checkbox filters
        peer_review = filter_args.get("wp_peer_review")
        model_availability = filter_args.get("wp_model_availability")
        data_availability = filter_args.get("wp_data_availability")
        uncertainty_quantification = filter_args.get("wp_uncertainty_quantification")
        sensitivity_analysis = filter_args.get("wp_sensitivity_analysis")
        analytical_rigor = filter_args.get("wp_analytical_rigor")
        results_validation = filter_args.get("wp_results_validation")
        granularity = filter_args.get("wp_granularity")
        completeness = filter_args.get("wp_completeness")
        technology_correlation = filter_args.get("wp_technology_correlation")
        geographical_correlation = filter_args.get("wp_geographical_correlation")
        temporal_correlation = filter_args.get("wp_temporal_correlation")

        # CITATION OPTIONS: Apply all filters EXCEPT citation
        citation_base = df.copy()
        if year_of_publication:
            citation_base = citation_base[
                citation_base["year_of_publication"].isin(year_of_publication)
            ]
        if publisher_institution_type_s_:
            citation_base = apply_multi_value_filter(
                citation_base,
                "publisher_institution_type_s_",
                publisher_institution_type_s_,
            )
        if author_institution_type_s_:
            citation_base = apply_multi_value_filter(
                citation_base, "author_institution_type_s_", author_institution_type_s_
            )
        if wp_study_region:
            citation_base = apply_multi_value_filter(
                citation_base, "region", wp_study_region
            )
        if data_center_type_s_:
            citation_base = apply_multi_value_filter(
                citation_base, "data_center_type_s_", data_center_type_s_
            )
        if associated_granularity:
            citation_base = apply_multi_value_filter(
                citation_base, "associated_granularity", associated_granularity
            )
        if modeling_approach_es_:
            citation_base = apply_multi_value_filter(
                citation_base, "modeling_approach_es_", modeling_approach_es_
            )
        if input_data_type_s_:
            citation_base = apply_multi_value_filter(
                citation_base, "input_data_type_s_", input_data_type_s_
            )
        if time_horizon:
            citation_base = citation_base[
                citation_base["time_horizon"].isin(time_horizon)
            ]
        if projection_narrative_s_:
            citation_base = apply_multi_value_filter(
                citation_base, "projection_narrative_s_", projection_narrative_s_
            )
        if label:
            citation_base = citation_base[citation_base["label"].isin(label)]
        if total_quality_rating and len(total_quality_rating) == 2:
            min_val, max_val = total_quality_rating
            citation_base = citation_base[
                (citation_base["total"] >= min_val)
                & (citation_base["total"] <= max_val)
            ]
        # Apply checkbox filters to constrain dropdown options
        if peer_review:
            citation_base = apply_checkbox_filter(
                citation_base, "peer_review", peer_review
            )
        if model_availability:
            citation_base = apply_checkbox_filter(
                citation_base, "model_availability", model_availability
            )
        if data_availability:
            citation_base = apply_checkbox_filter(
                citation_base, "data_availability", data_availability
            )
        if uncertainty_quantification:
            citation_base = apply_checkbox_filter(
                citation_base, "uncertainty_quantification", uncertainty_quantification
            )
        if sensitivity_analysis:
            citation_base = apply_checkbox_filter(
                citation_base, "sensitivity_analysis", sensitivity_analysis
            )
        if analytical_rigor:
            citation_base = apply_checkbox_filter(
                citation_base, "analytical_rigor", analytical_rigor
            )
        if results_validation:
            citation_base = apply_checkbox_filter(
                citation_base, "results_validation", results_validation
            )
        if granularity:
            citation_base = apply_checkbox_filter(
                citation_base, "granularity", granularity
            )
        if completeness:
            citation_base = apply_checkbox_filter(
                citation_base, "completeness", completeness
            )
        if technology_correlation:
            citation_base = apply_checkbox_filter(
                citation_base, "technology_correlation", technology_correlation
            )
        if geographical_correlation:
            citation_base = apply_checkbox_filter(
                citation_base, "geographical_correlation", geographical_correlation
            )
        if temporal_correlation:
            citation_base = apply_checkbox_filter(
                citation_base, "temporal_correlation", temporal_correlation
            )

        wp_citation_opts = get_single_value_options(citation_base, "citation")

        # YEAR OPTIONS: Apply all filters EXCEPT year
        year_base = df.copy()
        if citation:
            year_base = year_base[year_base["citation"].isin(citation)]
        if publisher_institution_type_s_:
            year_base = apply_multi_value_filter(
                year_base,
                "publisher_institution_type_s_",
                publisher_institution_type_s_,
            )
        if author_institution_type_s_:
            year_base = apply_multi_value_filter(
                year_base, "author_institution_type_s_", author_institution_type_s_
            )
        if wp_study_region:
            year_base = apply_multi_value_filter(year_base, "region", wp_study_region)
        if data_center_type_s_:
            year_base = apply_multi_value_filter(
                year_base, "data_center_type_s_", data_center_type_s_
            )
        if associated_granularity:
            year_base = apply_multi_value_filter(
                year_base, "associated_granularity", associated_granularity
            )
        if modeling_approach_es_:
            year_base = apply_multi_value_filter(
                year_base, "modeling_approach_es_", modeling_approach_es_
            )
        if input_data_type_s_:
            year_base = apply_multi_value_filter(
                year_base, "input_data_type_s_", input_data_type_s_
            )
        if time_horizon:
            year_base = year_base[year_base["time_horizon"].isin(time_horizon)]
        if projection_narrative_s_:
            year_base = apply_multi_value_filter(
                year_base, "projection_narrative_s_", projection_narrative_s_
            )
        if label:
            year_base = year_base[year_base["label"].isin(label)]
        if total_quality_rating and len(total_quality_rating) == 2:
            min_val, max_val = total_quality_rating
            year_base = year_base[
                (year_base["total"] >= min_val) & (year_base["total"] <= max_val)
            ]
        # Apply checkbox filters to constrain dropdown options
        if peer_review:
            year_base = apply_checkbox_filter(year_base, "peer_review", peer_review)
        if model_availability:
            year_base = apply_checkbox_filter(
                year_base, "model_availability", model_availability
            )
        if data_availability:
            year_base = apply_checkbox_filter(
                year_base, "data_availability", data_availability
            )
        if uncertainty_quantification:
            year_base = apply_checkbox_filter(
                year_base, "uncertainty_quantification", uncertainty_quantification
            )
        if sensitivity_analysis:
            year_base = apply_checkbox_filter(
                year_base, "sensitivity_analysis", sensitivity_analysis
            )
        if analytical_rigor:
            year_base = apply_checkbox_filter(
                year_base, "analytical_rigor", analytical_rigor
            )
        if results_validation:
            year_base = apply_checkbox_filter(
                year_base, "results_validation", results_validation
            )
        if granularity:
            year_base = apply_checkbox_filter(year_base, "granularity", granularity)
        if completeness:
            year_base = apply_checkbox_filter(year_base, "completeness", completeness)
        if technology_correlation:
            year_base = apply_checkbox_filter(
                year_base, "technology_correlation", technology_correlation
            )
        if geographical_correlation:
            year_base = apply_checkbox_filter(
                year_base, "geographical_correlation", geographical_correlation
            )
        if temporal_correlation:
            year_base = apply_checkbox_filter(
                year_base, "temporal_correlation", temporal_correlation
            )

        wp_pub_year_opts = get_single_value_options(year_base, "year_of_publication")

        # PUBLISHER OPTIONS: Apply all filters EXCEPT publisher
        publisher_base = df.copy()
        if citation:
            publisher_base = publisher_base[publisher_base["citation"].isin(citation)]
        if year_of_publication:
            publisher_base = publisher_base[
                publisher_base["year_of_publication"].isin(year_of_publication)
            ]
        if author_institution_type_s_:
            publisher_base = apply_multi_value_filter(
                publisher_base, "author_institution_type_s_", author_institution_type_s_
            )
        if wp_study_region:
            publisher_base = apply_multi_value_filter(
                publisher_base, "region", wp_study_region
            )
        if data_center_type_s_:
            publisher_base = apply_multi_value_filter(
                publisher_base, "data_center_type_s_", data_center_type_s_
            )
        if associated_granularity:
            publisher_base = apply_multi_value_filter(
                publisher_base, "associated_granularity", associated_granularity
            )
        if modeling_approach_es_:
            publisher_base = apply_multi_value_filter(
                publisher_base, "modeling_approach_es_", modeling_approach_es_
            )
        if input_data_type_s_:
            publisher_base = apply_multi_value_filter(
                publisher_base, "input_data_type_s_", input_data_type_s_
            )
        if time_horizon:
            publisher_base = publisher_base[
                publisher_base["time_horizon"].isin(time_horizon)
            ]
        if projection_narrative_s_:
            publisher_base = apply_multi_value_filter(
                publisher_base, "projection_narrative_s_", projection_narrative_s_
            )
        if label:
            publisher_base = publisher_base[publisher_base["label"].isin(label)]
        if total_quality_rating and len(total_quality_rating) == 2:
            min_val, max_val = total_quality_rating
            publisher_base = publisher_base[
                (publisher_base["total"] >= min_val)
                & (publisher_base["total"] <= max_val)
            ]
        # Apply checkbox filters to constrain dropdown options
        if peer_review:
            publisher_base = apply_checkbox_filter(
                publisher_base, "peer_review", peer_review
            )
        if model_availability:
            publisher_base = apply_checkbox_filter(
                publisher_base, "model_availability", model_availability
            )
        if data_availability:
            publisher_base = apply_checkbox_filter(
                publisher_base, "data_availability", data_availability
            )
        if uncertainty_quantification:
            publisher_base = apply_checkbox_filter(
                publisher_base, "uncertainty_quantification", uncertainty_quantification
            )
        if sensitivity_analysis:
            publisher_base = apply_checkbox_filter(
                publisher_base, "sensitivity_analysis", sensitivity_analysis
            )
        if analytical_rigor:
            publisher_base = apply_checkbox_filter(
                publisher_base, "analytical_rigor", analytical_rigor
            )
        if results_validation:
            publisher_base = apply_checkbox_filter(
                publisher_base, "results_validation", results_validation
            )
        if granularity:
            publisher_base = apply_checkbox_filter(
                publisher_base, "granularity", granularity
            )
        if completeness:
            publisher_base = apply_checkbox_filter(
                publisher_base, "completeness", completeness
            )
        if technology_correlation:
            publisher_base = apply_checkbox_filter(
                publisher_base, "technology_correlation", technology_correlation
            )
        if geographical_correlation:
            publisher_base = apply_checkbox_filter(
                publisher_base, "geographical_correlation", geographical_correlation
            )
        if temporal_correlation:
            publisher_base = apply_checkbox_filter(
                publisher_base, "temporal_correlation", temporal_correlation
            )

        wp_publisher_opts = get_multi_value_options(
            publisher_base, "publisher_institution_type_s_"
        )

        # AUTHOR OPTIONS: Apply all filters EXCEPT author
        author_base = df.copy()
        if citation:
            author_base = author_base[author_base["citation"].isin(citation)]
        if year_of_publication:
            author_base = author_base[
                author_base["year_of_publication"].isin(year_of_publication)
            ]
        if publisher_institution_type_s_:
            author_base = apply_multi_value_filter(
                author_base,
                "publisher_institution_type_s_",
                publisher_institution_type_s_,
            )
        if wp_study_region:
            author_base = apply_multi_value_filter(
                author_base, "region", wp_study_region
            )
        if data_center_type_s_:
            author_base = apply_multi_value_filter(
                author_base, "data_center_type_s_", data_center_type_s_
            )
        if associated_granularity:
            author_base = apply_multi_value_filter(
                author_base, "associated_granularity", associated_granularity
            )
        if modeling_approach_es_:
            author_base = apply_multi_value_filter(
                author_base, "modeling_approach_es_", modeling_approach_es_
            )
        if input_data_type_s_:
            author_base = apply_multi_value_filter(
                author_base, "input_data_type_s_", input_data_type_s_
            )
        if time_horizon:
            author_base = author_base[author_base["time_horizon"].isin(time_horizon)]
        if projection_narrative_s_:
            author_base = apply_multi_value_filter(
                author_base, "projection_narrative_s_", projection_narrative_s_
            )
        if label:
            author_base = author_base[author_base["label"].isin(label)]
        if total_quality_rating and len(total_quality_rating) == 2:
            min_val, max_val = total_quality_rating
            author_base = author_base[
                (author_base["total"] >= min_val) & (author_base["total"] <= max_val)
            ]
        # Apply checkbox filters to constrain dropdown options
        if peer_review:
            author_base = apply_checkbox_filter(author_base, "peer_review", peer_review)
        if model_availability:
            author_base = apply_checkbox_filter(
                author_base, "model_availability", model_availability
            )
        if data_availability:
            author_base = apply_checkbox_filter(
                author_base, "data_availability", data_availability
            )
        if uncertainty_quantification:
            author_base = apply_checkbox_filter(
                author_base, "uncertainty_quantification", uncertainty_quantification
            )
        if sensitivity_analysis:
            author_base = apply_checkbox_filter(
                author_base, "sensitivity_analysis", sensitivity_analysis
            )
        if analytical_rigor:
            author_base = apply_checkbox_filter(
                author_base, "analytical_rigor", analytical_rigor
            )
        if results_validation:
            author_base = apply_checkbox_filter(
                author_base, "results_validation", results_validation
            )
        if granularity:
            author_base = apply_checkbox_filter(author_base, "granularity", granularity)
        if completeness:
            author_base = apply_checkbox_filter(
                author_base, "completeness", completeness
            )
        if technology_correlation:
            author_base = apply_checkbox_filter(
                author_base, "technology_correlation", technology_correlation
            )
        if geographical_correlation:
            author_base = apply_checkbox_filter(
                author_base, "geographical_correlation", geographical_correlation
            )
        if temporal_correlation:
            author_base = apply_checkbox_filter(
                author_base, "temporal_correlation", temporal_correlation
            )

        wp_author_opts = get_multi_value_options(
            author_base, "author_institution_type_s_"
        )

        # For remaining filters, apply ALL current filters (they depend on everything)
        dependent_base = df.copy()
        if citation:
            dependent_base = dependent_base[dependent_base["citation"].isin(citation)]
        if year_of_publication:
            dependent_base = dependent_base[
                dependent_base["year_of_publication"].isin(year_of_publication)
            ]
        if publisher_institution_type_s_:
            dependent_base = apply_multi_value_filter(
                dependent_base,
                "publisher_institution_type_s_",
                publisher_institution_type_s_,
            )
        if author_institution_type_s_:
            dependent_base = apply_multi_value_filter(
                dependent_base, "author_institution_type_s_", author_institution_type_s_
            )
        if wp_study_region:
            dependent_base = apply_multi_value_filter(
                dependent_base, "region", wp_study_region
            )
        if data_center_type_s_:
            dependent_base = apply_multi_value_filter(
                dependent_base, "data_center_type_s_", data_center_type_s_
            )
        if associated_granularity:
            dependent_base = apply_multi_value_filter(
                dependent_base, "associated_granularity", associated_granularity
            )
        if modeling_approach_es_:
            dependent_base = apply_multi_value_filter(
                dependent_base, "modeling_approach_es_", modeling_approach_es_
            )
        if input_data_type_s_:
            dependent_base = apply_multi_value_filter(
                dependent_base, "input_data_type_s_", input_data_type_s_
            )
        if time_horizon:
            dependent_base = dependent_base[
                dependent_base["time_horizon"].isin(time_horizon)
            ]
        if projection_narrative_s_:
            dependent_base = apply_multi_value_filter(
                dependent_base, "projection_narrative_s_", projection_narrative_s_
            )
        if label:
            dependent_base = dependent_base[dependent_base["label"].isin(label)]
        if total_quality_rating and len(total_quality_rating) == 2:
            min_val, max_val = total_quality_rating
            dependent_base = dependent_base[
                (dependent_base["total"] >= min_val)
                & (dependent_base["total"] <= max_val)
            ]
        # Apply checkbox filters
        if peer_review:
            dependent_base = dependent_base[
                dependent_base["peer_review"].isin(peer_review)
            ]
        if model_availability:
            dependent_base = dependent_base[
                dependent_base["model_availability"].isin(model_availability)
            ]
        if data_availability:
            dependent_base = dependent_base[
                dependent_base["data_availability"].isin(data_availability)
            ]
        if uncertainty_quantification:
            dependent_base = dependent_base[
                dependent_base["uncertainty_quantification"].isin(
                    uncertainty_quantification
                )
            ]
        if sensitivity_analysis:
            dependent_base = dependent_base[
                dependent_base["sensitivity_analysis"].isin(sensitivity_analysis)
            ]
        if analytical_rigor:
            dependent_base = dependent_base[
                dependent_base["analytical_rigor"].isin(analytical_rigor)
            ]
        if results_validation:
            dependent_base = dependent_base[
                dependent_base["results_validation"].isin(results_validation)
            ]
        if granularity:
            dependent_base = dependent_base[
                dependent_base["granularity"].isin(granularity)
            ]
        if completeness:
            dependent_base = dependent_base[
                dependent_base["completeness"].isin(completeness)
            ]
        if technology_correlation:
            dependent_base = dependent_base[
                dependent_base["technology_correlation"].isin(technology_correlation)
            ]
        if geographical_correlation:
            dependent_base = dependent_base[
                dependent_base["geographical_correlation"].isin(
                    geographical_correlation
                )
            ]
        if temporal_correlation:
            dependent_base = dependent_base[
                dependent_base["temporal_correlation"].isin(temporal_correlation)
            ]

        # Generate dependent options - each filter excludes itself from the base

        # TIME HORIZON OPTIONS: Apply all filters EXCEPT time_horizon
        time_horizon_base = df.copy()
        if citation:
            time_horizon_base = time_horizon_base[
                time_horizon_base["citation"].isin(citation)
            ]
        if year_of_publication:
            time_horizon_base = time_horizon_base[
                time_horizon_base["year_of_publication"].isin(year_of_publication)
            ]
        if publisher_institution_type_s_:
            time_horizon_base = apply_multi_value_filter(
                time_horizon_base,
                "publisher_institution_type_s_",
                publisher_institution_type_s_,
            )
        if author_institution_type_s_:
            time_horizon_base = apply_multi_value_filter(
                time_horizon_base,
                "author_institution_type_s_",
                author_institution_type_s_,
            )
        if wp_study_region:
            time_horizon_base = apply_multi_value_filter(
                time_horizon_base, "region", wp_study_region
            )
        if data_center_type_s_:
            time_horizon_base = apply_multi_value_filter(
                time_horizon_base, "data_center_type_s_", data_center_type_s_
            )
        if associated_granularity:
            time_horizon_base = apply_multi_value_filter(
                time_horizon_base, "associated_granularity", associated_granularity
            )
        if modeling_approach_es_:
            time_horizon_base = apply_multi_value_filter(
                time_horizon_base, "modeling_approach_es_", modeling_approach_es_
            )
        if input_data_type_s_:
            time_horizon_base = apply_multi_value_filter(
                time_horizon_base, "input_data_type_s_", input_data_type_s_
            )
        # Skip time_horizon itself
        if projection_narrative_s_:
            time_horizon_base = apply_multi_value_filter(
                time_horizon_base, "projection_narrative_s_", projection_narrative_s_
            )
        if label:
            time_horizon_base = time_horizon_base[
                time_horizon_base["label"].isin(label)
            ]
        # Apply checkbox filters
        checkbox_map = {
            "wp_peer_review": peer_review,
            "wp_model_availability": model_availability,
            "wp_data_availability": data_availability,
            "wp_uncertainty_quantification": uncertainty_quantification,
            "wp_sensitivity_analysis": sensitivity_analysis,
            "wp_analytical_rigor": analytical_rigor,
            "wp_results_validation": results_validation,
            "wp_granularity": granularity,
            "wp_completeness": completeness,
            "wp_technology_correlation": technology_correlation,
            "wp_geographical_correlation": geographical_correlation,
            "wp_temporal_correlation": temporal_correlation,
        }
        for checkbox_filter in WATER_PROJECTION_CHECKLIST_FILTERS:
            checkbox_name = checkbox_filter.replace(
                "wp_", ""
            )  # Remove prefix for column name
            checkbox_values = checkbox_map.get(checkbox_filter)
            if checkbox_values:
                time_horizon_base = apply_checkbox_filter(
                    time_horizon_base, checkbox_name, checkbox_values
                )

        wp_time_horizon_opts = get_single_value_options(
            time_horizon_base, "time_horizon"
        )

        # PROJECTION NARRATIVE OPTIONS: Apply all filters EXCEPT projection_narrative_s_
        projection_narrative_base = df.copy()
        if citation:
            projection_narrative_base = projection_narrative_base[
                projection_narrative_base["citation"].isin(citation)
            ]
        if year_of_publication:
            projection_narrative_base = projection_narrative_base[
                projection_narrative_base["year_of_publication"].isin(
                    year_of_publication
                )
            ]
        if publisher_institution_type_s_:
            projection_narrative_base = apply_multi_value_filter(
                projection_narrative_base,
                "publisher_institution_type_s_",
                publisher_institution_type_s_,
            )
        if author_institution_type_s_:
            projection_narrative_base = apply_multi_value_filter(
                projection_narrative_base,
                "author_institution_type_s_",
                author_institution_type_s_,
            )
        if wp_study_region:
            projection_narrative_base = apply_multi_value_filter(
                projection_narrative_base, "region", wp_study_region
            )
        if data_center_type_s_:
            projection_narrative_base = apply_multi_value_filter(
                projection_narrative_base, "data_center_type_s_", data_center_type_s_
            )
        if associated_granularity:
            projection_narrative_base = apply_multi_value_filter(
                projection_narrative_base,
                "associated_granularity",
                associated_granularity,
            )
        if modeling_approach_es_:
            projection_narrative_base = apply_multi_value_filter(
                projection_narrative_base,
                "modeling_approach_es_",
                modeling_approach_es_,
            )
        if input_data_type_s_:
            projection_narrative_base = apply_multi_value_filter(
                projection_narrative_base, "input_data_type_s_", input_data_type_s_
            )
        if time_horizon:
            projection_narrative_base = projection_narrative_base[
                projection_narrative_base["time_horizon"].isin(time_horizon)
            ]
        # Skip projection_narrative_s_ itself
        if label:
            projection_narrative_base = projection_narrative_base[
                projection_narrative_base["label"].isin(label)
            ]
        # Apply checkbox filters
        checkbox_map = {
            "wp_peer_review": peer_review,
            "wp_model_availability": model_availability,
            "wp_data_availability": data_availability,
            "wp_uncertainty_quantification": uncertainty_quantification,
            "wp_sensitivity_analysis": sensitivity_analysis,
            "wp_analytical_rigor": analytical_rigor,
            "wp_results_validation": results_validation,
            "wp_granularity": granularity,
            "wp_completeness": completeness,
            "wp_technology_correlation": technology_correlation,
            "wp_geographical_correlation": geographical_correlation,
            "wp_temporal_correlation": temporal_correlation,
        }
        for checkbox_filter in WATER_PROJECTION_CHECKLIST_FILTERS:
            checkbox_name = checkbox_filter.replace(
                "wp_", ""
            )  # Remove prefix for column name
            checkbox_values = checkbox_map.get(checkbox_filter)
            if checkbox_values:
                projection_narrative_base = apply_checkbox_filter(
                    projection_narrative_base, checkbox_name, checkbox_values
                )

        wp_projection_narrative_opts = get_multi_value_options(
            projection_narrative_base, "projection_narrative_s_"
        )

        # LABEL OPTIONS: Apply all filters EXCEPT label
        label_base = df.copy()
        if citation:
            label_base = label_base[label_base["citation"].isin(citation)]
        if year_of_publication:
            label_base = label_base[
                label_base["year_of_publication"].isin(year_of_publication)
            ]
        if publisher_institution_type_s_:
            label_base = apply_multi_value_filter(
                label_base,
                "publisher_institution_type_s_",
                publisher_institution_type_s_,
            )
        if author_institution_type_s_:
            label_base = apply_multi_value_filter(
                label_base,
                "author_institution_type_s_",
                author_institution_type_s_,
            )
        if wp_study_region:
            label_base = apply_multi_value_filter(label_base, "region", wp_study_region)
        if data_center_type_s_:
            label_base = apply_multi_value_filter(
                label_base, "data_center_type_s_", data_center_type_s_
            )
        if associated_granularity:
            label_base = apply_multi_value_filter(
                label_base, "associated_granularity", associated_granularity
            )
        if modeling_approach_es_:
            label_base = apply_multi_value_filter(
                label_base, "modeling_approach_es_", modeling_approach_es_
            )
        if input_data_type_s_:
            label_base = apply_multi_value_filter(
                label_base, "input_data_type_s_", input_data_type_s_
            )
        if time_horizon:
            label_base = label_base[label_base["time_horizon"].isin(time_horizon)]
        if projection_narrative_s_:
            label_base = apply_multi_value_filter(
                label_base, "projection_narrative_s_", projection_narrative_s_
            )
        # Skip label itself
        # Apply checkbox filters
        checkbox_map = {
            "wp_peer_review": peer_review,
            "wp_model_availability": model_availability,
            "wp_data_availability": data_availability,
            "wp_uncertainty_quantification": uncertainty_quantification,
            "wp_sensitivity_analysis": sensitivity_analysis,
            "wp_analytical_rigor": analytical_rigor,
            "wp_results_validation": results_validation,
            "wp_granularity": granularity,
            "wp_completeness": completeness,
            "wp_technology_correlation": technology_correlation,
            "wp_geographical_correlation": geographical_correlation,
            "wp_temporal_correlation": temporal_correlation,
        }
        for checkbox_filter in WATER_PROJECTION_CHECKLIST_FILTERS:
            checkbox_name = checkbox_filter.replace(
                "wp_", ""
            )  # Remove prefix for column name
            checkbox_values = checkbox_map.get(checkbox_filter)
            if checkbox_values:
                label_base = apply_checkbox_filter(
                    label_base, checkbox_name, checkbox_values
                )

        wp_label_opts = get_single_value_options(label_base, "label")

        # OTHER DEPENDENT OPTIONS (using original dependent_base logic)
        wp_study_region_opts = get_multi_value_options(dependent_base, "region")
        wp_data_center_type_opts = get_multi_value_options(
            dependent_base, "data_center_type_s_"
        )
        wp_associated_granularity_opts = get_multi_value_options(
            dependent_base, "associated_granularity"
        )
        wp_modeling_approach_opts = get_multi_value_options(
            dependent_base, "modeling_approach_es_"
        )
        wp_input_data_type_opts = get_multi_value_options(
            dependent_base, "input_data_type_s_"
        )

        # CHECKBOX OPTIONS: Each checkbox excludes itself from filtering (like dropdowns)
        def get_checkbox_base_excluding(exclude_filter):
            """Get base dataframe with all filters applied except the specified checkbox filter"""
            base = df.copy()
            # Apply all dropdown filters
            if citation:
                base = base[base["citation"].isin(citation)]
            if year_of_publication:
                base = base[base["year_of_publication"].isin(year_of_publication)]
            if publisher_institution_type_s_:
                base = apply_multi_value_filter(
                    base, "publisher_institution_type_s_", publisher_institution_type_s_
                )
            if author_institution_type_s_:
                base = apply_multi_value_filter(
                    base, "author_institution_type_s_", author_institution_type_s_
                )
            if wp_study_region:
                base = apply_multi_value_filter(base, "region", wp_study_region)
            if data_center_type_s_:
                base = apply_multi_value_filter(
                    base, "data_center_type_s_", data_center_type_s_
                )
            if associated_granularity:
                base = apply_multi_value_filter(
                    base, "associated_granularity", associated_granularity
                )
            if modeling_approach_es_:
                base = apply_multi_value_filter(
                    base, "modeling_approach_es_", modeling_approach_es_
                )
            if input_data_type_s_:
                base = apply_multi_value_filter(
                    base, "input_data_type_s_", input_data_type_s_
                )
            if time_horizon:
                base = base[base["time_horizon"].isin(time_horizon)]
            if projection_narrative_s_:
                base = apply_multi_value_filter(
                    base, "projection_narrative_s_", projection_narrative_s_
                )
            if label:
                base = base[base["label"].isin(label)]
            if total_quality_rating and len(total_quality_rating) == 2:
                min_val, max_val = total_quality_rating
                base = base[(base["total"] >= min_val) & (base["total"] <= max_val)]

            # Apply checkbox filters excluding the specified one
            exclude_filter_name = (
                exclude_filter.replace("wp_", "")
                if exclude_filter.startswith("wp_")
                else exclude_filter
            )
            if exclude_filter_name != "peer_review" and peer_review:
                base = base[base["peer_review"].isin(peer_review)]
            if exclude_filter_name != "model_availability" and model_availability:
                base = base[base["model_availability"].isin(model_availability)]
            if exclude_filter_name != "data_availability" and data_availability:
                base = base[base["data_availability"].isin(data_availability)]
            if (
                exclude_filter_name != "uncertainty_quantification"
                and uncertainty_quantification
            ):
                base = base[
                    base["uncertainty_quantification"].isin(uncertainty_quantification)
                ]
            if exclude_filter_name != "sensitivity_analysis" and sensitivity_analysis:
                base = base[base["sensitivity_analysis"].isin(sensitivity_analysis)]
            if exclude_filter_name != "analytical_rigor" and analytical_rigor:
                base = base[base["analytical_rigor"].isin(analytical_rigor)]
            if exclude_filter_name != "results_validation" and results_validation:
                base = base[base["results_validation"].isin(results_validation)]
            if exclude_filter_name != "granularity" and granularity:
                base = base[base["granularity"].isin(granularity)]
            if exclude_filter_name != "completeness" and completeness:
                base = base[base["completeness"].isin(completeness)]
            if (
                exclude_filter_name != "technology_correlation"
                and technology_correlation
            ):
                base = base[base["technology_correlation"].isin(technology_correlation)]
            if (
                exclude_filter_name != "geographical_correlation"
                and geographical_correlation
            ):
                base = base[
                    base["geographical_correlation"].isin(geographical_correlation)
                ]
            if exclude_filter_name != "temporal_correlation" and temporal_correlation:
                base = base[base["temporal_correlation"].isin(temporal_correlation)]

            return base

        return (
            wp_citation_opts,  # 1 - citation
            wp_pub_year_opts,  # 2 - year_of_publication
            wp_publisher_opts,  # 3 - publisher_institution_type_s_
            wp_author_opts,  # 4 - author_institution_type_s_
            wp_study_region_opts,  # 17 - study_region
            wp_data_center_type_opts,  # 18 - data_center_type_s_
            wp_associated_granularity_opts,  # 19 - associated_granularity
            wp_modeling_approach_opts,  # 20 - modeling_approach_es_
            wp_input_data_type_opts,  # 21 - input_data_type_s_
            wp_time_horizon_opts,  # 22 - time_horizon
            wp_projection_narrative_opts,  # 23 - projection_narrative_s_
            wp_label_opts,  # 24 - label
        )

    # Update chart
    @app.callback(
        Output("wp-chart-container", "children"),
        [
            Input("wp-apply-filters-btn", "n_clicks"),
            Input("wp-clear-filters-btn", "n_clicks"),
            Input("wp_units", "value"),
        ],
        [State(name, "value") for name in WATER_PROJECTION_INPUT_FILTERS],
        prevent_initial_call=False,
    )
    def update_dashboard_on_button_click(
        apply_clicks, clear_clicks, units_value, *filter_values
    ):
        filter_args = dict(zip(WATER_PROJECTION_INPUT_FILTERS, filter_values))
        filter_args["wp_units"] = units_value

        print(f"\n=== CHART CALLBACK DEBUG ===")
        print(f"Apply clicks: {apply_clicks}, Clear clicks: {clear_clicks}")
        print(f"Units: {units_value}")
        print(f"Citation: {filter_args.get('citation')}")
        print(f"Total quality rating: {filter_args.get('total_quality_rating')}")

        ctx = dash.callback_context
        if ctx.triggered:
            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

            if trigger_id == "wp-clear-filters-btn":
                # Even when clearing, apply units filter
                filtered_df = df[df["units"] == units_value].copy()
                filters_applied = False
            elif trigger_id in ["wp-apply-filters-btn", "wp_units"]:
                filtered_df = filter_data(df, **filter_args)
                filters_applied = any(
                    filter_args[name]
                    for name in WATER_PROJECTION_INPUT_FILTERS
                    if name != "wp_units"
                    and filter_args[name] not in [None, [], [12, 36]]
                )
            else:
                # Initial load or units change
                filtered_df = df[df["units"] == units_value].copy()
                filters_applied = False
        else:
            # Initial load
            filtered_df = df[df["units"] == units_value].copy()
            filters_applied = False

        print(f"Chart callback received {len(filtered_df)} records")

        filtered_df = filtered_df[filtered_df["energy_demand"].notna()]

        # Add this debugging right after line 1547

        # Create the full dataset for background (filtered by units)
        chart_full_df = df[df["units"] == units_value].copy()
        # Generate chart based on units
        if units_value == "TWh":
            chart_fig = create_water_projections_line_plot(
                filtered_df=filtered_df,
                full_df=chart_full_df,
                filters_applied=filters_applied,
                yaxis_title="Water Demand (L/kWh)",
                y_label="Water Demand (L/kWh)",
            )
            chart_id = "water-projections-line-chart"
            title = "Water Demand Estimates & Projections (L/kWh)"
            section_id = "water-projections-section"
            expand_id = "expand-water-projections"
            filename = "water_projections"
        else:  # L/kWh or other units
            chart_fig = create_water_projections_line_plot(
                filtered_df=filtered_df,
                full_df=chart_full_df,
                filters_applied=filters_applied,
                yaxis_title=f"Water Demand ({units_value})",
                y_label=f"Water Demand ({units_value})",
            )
            chart_id = "water-projections-line-chart"
            title = f"Water Demand Estimates & Projections ({units_value})"
            section_id = "water-projections-section"
            expand_id = "expand-water-projections"
            filename = "water_projections"

        accordion_children = [
            dcc.Markdown("""
                    To be added...
                    """)
        ]
        accordion_title = html.Span(
            [
                "What Do Water Projections Tell Us?",
                html.Span(" Read more...", className="text-link"),
            ]
        )
        # Create the return value
        return html.Div(
            [
                html.A(id=section_id),
                create_chart_row(
                    chart_id=chart_id,
                    title=title,
                    expand_id=expand_id,
                    accordion_children=accordion_children,
                    accordion_title=accordion_title,
                    filename=filename,
                    figure=chart_fig,
                ),
            ],
            style={"margin": "35px 0"},
        )

    @app.callback(
        [
            Output("water-graph-modal", "is_open"),
            Output("water-modal-title", "children"),
            Output("water-expanded-graph", "figure"),
        ],
        [
            Input("expand-water-projections", "n_clicks"),
        ],
        [
            State("water-graph-modal", "is_open"),
            State("water-projections-line-chart", "figure"),
        ],
        prevent_initial_call=True,
    )
    def toggle_modal(expand_clicks, is_open, chart_figure):
        if not expand_clicks:
            raise dash.exceptions.PreventUpdate

        title = "Water Projections"
        if chart_figure and "layout" in chart_figure:
            ytitle = chart_figure["layout"].get("yaxis", {}).get("title")
            if isinstance(ytitle, dict):
                ytitle = ytitle.get("text")
            if isinstance(ytitle, str):
                if "L/kWh" in ytitle:
                    title = "Water Demand Estimates and Projections (L/kWh ?)"
        return (not is_open, title, chart_figure or {})

    # Download callbacks
    @app.callback(
        Output("download-water-projections-line-chart", "data"),
        Input("download-btn-water-projections-line-chart", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_water_projections_data(n_clicks):
        # Get the project root directory (2 levels up from callbacks directory)
        root_dir = Path(__file__).parent.parent.parent
        input_path = root_dir / "data" / "DCEWM-PUEDataset.xlsx"

        # Debug print
        print(f"Looking for file at: {input_path}")
        print(f"File exists: {input_path.exists()}")

        return create_filtered_excel_download(
            input_path=input_path,
            output_filename="water_projections_data.xlsx",
            sheets_to_export=[
                "PUE",
                "Read Me",
            ],
            internal_prefix="_internal_",
            # skip_rows=1,
            n_clicks=n_clicks,
        )
