import dash
from pathlib import Path
from dash import Dash, Input, Output, State, callback, dcc, html, callback_context
import pandas as pd
from charts.global_policies.stacked_area_chart import (
    create_global_policies_stacked_area_plot,
)
from components.excel_export import create_filtered_excel_download


def filter_data(
    df,
    gp_jurisdiction_level,
    gp_region,
    gp_country,
    gp_state,
    gp_county,
    gp_city,
    gp_order_type,
    gp_status,
    gp_instrument,
    gp_objective,
):
    """Filter dataframe based on all selections"""
    filtered_df = df.copy()

    # Standard single-value filters
    if gp_jurisdiction_level:
        filtered_df = filtered_df[
            filtered_df["jurisdiction_level"].isin(gp_jurisdiction_level)
        ]
    if gp_order_type:
        filtered_df = filtered_df[filtered_df["order_type"].isin(gp_order_type)]
    if gp_status:
        filtered_df = filtered_df[filtered_df["status"].isin(gp_status)]

    # Multi-value location fields (using apply_multi_value_filter if available, or simple isin)
    if gp_region:
        filtered_df = filtered_df[filtered_df["region"].isin(gp_region)]
    if gp_country:
        filtered_df = filtered_df[filtered_df["country"].isin(gp_country)]
    if gp_state:
        filtered_df = filtered_df[filtered_df["state_province"].isin(gp_state)]
    if gp_county:
        filtered_df = filtered_df[filtered_df["county"].isin(gp_county)]
    if gp_city:
        filtered_df = filtered_df[filtered_df["city"].isin(gp_city)]

    # Instrument and Objective filters - need to check both the column value AND has_instrument/has_objective
    # Since data is pivoted, we need to get policy_ids that match, then filter the full dataframe
    matching_policy_ids = None

    if gp_instrument:
        # Filter to rows where instrument matches AND has_instrument indicates "yes"
        # Convert has_instrument to string and check for truthy values
        has_instrument_true = (
            (filtered_df["has_instrument"] == True)
            | (filtered_df["has_instrument"] == 1)
            | (
                filtered_df["has_instrument"]
                .astype(str)
                .str.upper()
                .isin(["YES", "TRUE", "1"])
            )
        )
        instrument_mask = (
            filtered_df["instrument"].isin(gp_instrument) & has_instrument_true
        )
        # Get unique policy_ids that match the instrument filter
        matching_policy_ids = set(filtered_df[instrument_mask]["policy_id"].unique())

    if gp_objective:
        # Filter to rows where objective matches AND has_objective indicates "yes"
        has_objective_true = (
            (filtered_df["has_objective"] == True)
            | (filtered_df["has_objective"] == 1)
            | (
                filtered_df["has_objective"]
                .astype(str)
                .str.upper()
                .isin(["YES", "TRUE", "1"])
            )
        )
        objective_mask = (
            filtered_df["objective"].isin(gp_objective) & has_objective_true
        )
        # Get unique policy_ids that match the objective filter
        objective_policy_ids = set(filtered_df[objective_mask]["policy_id"].unique())

        # If instrument filter was also applied, intersect the sets (policies must match BOTH)
        # Otherwise, just use the objective policy_ids
        if matching_policy_ids is not None:
            matching_policy_ids = matching_policy_ids & objective_policy_ids
        else:
            matching_policy_ids = objective_policy_ids

    # Apply the policy_id filter if instrument or objective filters were used
    if matching_policy_ids is not None:
        filtered_df = filtered_df[filtered_df["policy_id"].isin(matching_policy_ids)]

    return filtered_df


def register_global_policies_area_callbacks():
    return fig
