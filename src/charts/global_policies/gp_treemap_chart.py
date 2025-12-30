import plotly.graph_objects as go
import textwrap
import pandas as pd


def get_abbreviation(text):
    """Get abbreviation from dictionary if available, otherwise return original text."""
    if not text:
        return ""
    text = str(text)
    abbrevs = {
        "Research, demonstration, and development": "R&D",
        "Other Environmental": "Other Environ.",
        "Development restrictions": "Dev. Restrictions",
        "Measurement and Reporting": "Measure & Report",
        "Development incentives": "Dev. Incentives",
        "United Kingdom": "UK",
        "Procurement standard": "Procurement Std.",
        "Performance standard": "Performance Std.",
    }
    return abbrevs.get(text, text)


def wrap_label(text, width=20):
    """Wrap text without breaking words. Only uses dictionary abbreviations, no truncation."""
    if not text:
        return ""
    # Only use dictionary abbreviations, don't truncate
    text = get_abbreviation(text)
    # Wrap text without breaking words
    wrapped = textwrap.wrap(
        str(text), width=width, break_long_words=False, break_on_hyphens=False
    )
    return "<br>".join(wrapped)


def build_treemap_data(df, path_cols, policy_col):
    """
    Build treemap data structure from preprocessed dataframe.

    Args:
        df: Preprocessed DataFrame with attr_type and attr_value columns (from preprocess_treemap_data)
        path_cols: List of columns defining hierarchy
                   e.g. ['region', 'country', 'jurisdiction_level', 'state_province', 'city', 'attr_type', 'attr_value']
        policy_col: Column containing policy IDs

    Returns: dict with ids, labels, parents, values, policy_ids_map, node_levels
    """
    nodes = {
        "world": {"label": "Global", "parent": "", "policies": set(), "policy_ids": []}
    }

    for _, row in df.iterrows():
        pid = row[policy_col]
        nodes["world"]["policies"].add(pid)
        current_parent = "world"

        for col in path_cols:
            val = row[col]
            if pd.isna(val) or str(val).strip().lower() in {"", "none", "nan", "n/a"}:
                continue

            node_id = f"{current_parent}/{val}"
            if node_id not in nodes:
                nodes[node_id] = {
                    "label": str(val),
                    "parent": current_parent,
                    "policies": set(),
                    "policy_ids": [],
                }
            nodes[node_id]["policies"].add(pid)
            nodes[node_id]["policy_ids"].append(pid)
            current_parent = node_id

    # Build output arrays
    ids, labels, parents, values = [], [], [], []
    policy_ids_map = {}
    node_levels = {}  # Store depth level for each node

    for nid, info in nodes.items():
        count = len(info["policies"])
        if count == 0:
            continue
        ids.append(nid)
        # Use wrap_label to wrap text without breaking words
        # Only abbreviates if in dictionary, otherwise uses full label
        label_txt = wrap_label(info["label"], width=20)
        # Put count on new line to allow better wrapping
        labels.append(f"{label_txt}<br>({count})")
        parents.append(info["parent"])
        values.append(count)
        # Store policy IDs for all nodes (useful for callbacks)
        if info["policy_ids"]:
            policy_ids_map[nid] = sorted(set(info["policy_ids"]))
        # Store node depth level
        node_levels[nid] = get_node_depth(nid)

    return {
        "ids": ids,
        "labels": labels,
        "parents": parents,
        "values": values,
        "policy_ids_map": policy_ids_map,
        "node_levels": node_levels,
    }


def get_node_depth(node_id):
    """
    Calculate the depth level of a node based on its ID.

    Node ID format: "world/level1/level2/level3/..."
    Examples:
    - "world" = depth 0 (root)
    - "world/North America" = depth 1 (region)
    - "world/North America/United States" = depth 2 (country)
    - "world/North America/United States/States" = depth 3 (jurisdiction_level)
    - "world/North America/United States/States/California" = depth 4 (state_province)
    """
    if not node_id or node_id == "world":
        return 0
    # Count the number of "/" separators to determine depth
    # "world/region" has 1 separator = depth 1
    # "world/region/country" has 2 separators = depth 2
    return len(node_id.split("/")) - 1


def calculate_maxdepth_for_node(node_id, path_cols):
    """
    Calculate appropriate maxdepth based on clicked node.
    Rules:
    - Level 2 (world/region/country): depth 3
    - Level 3 (world/region/country/jurisdiction_level): depth 2
    - Level 4+ (state_province and below): depth 3
    """
    depth = get_node_depth(node_id)

    if depth == 2:  # world/region/country
        return 3
    elif depth == 3:  # world/region/country/jurisdiction_level
        return 2
    elif depth >= 4:  # state_province and below
        return 3
    else:
        return 3  # default


def create_treemap_fig(
    data, clicked_node_id=None, maxdepth=None, policy_metadata_df=None
):
    """
    Create treemap figure with dynamic depth and labels.

    Args:
        data: Treemap data dict with ids, labels, parents, values, policy_ids_map
        clicked_node_id: Node ID that was clicked (for depth calculation)
        maxdepth: Override maxdepth (if None, calculated from clicked_node_id)
        policy_metadata_df: DataFrame with policy metadata for displaying policy details
    """
    # Set root to clicked node for drill-down, or "world" if no click
    root_id = (
        clicked_node_id
        if clicked_node_id and clicked_node_id in data["ids"]
        else "world"
    )

    # Filter data to show only the subtree starting from root_id
    # This implements drill-down by showing only descendants of the clicked node
    if root_id != "world":
        # Find all nodes that are descendants of root_id (including root_id itself)
        filtered_indices = []
        for i, node_id in enumerate(data["ids"]):
            # Include the root node itself
            if node_id == root_id:
                filtered_indices.append(i)
            # Include all nodes whose parent path includes root_id
            elif node_id.startswith(root_id + "/"):
                filtered_indices.append(i)

        # Filter all data arrays
        filtered_ids = [data["ids"][i] for i in filtered_indices]
        filtered_labels = [data["labels"][i] for i in filtered_indices]
        filtered_parents = []
        filtered_values = [data["values"][i] for i in filtered_indices]

        # Adjust parents: if parent is outside the filtered set, make it the root
        for i in filtered_indices:
            parent = data["parents"][i]
            if parent == "" or parent not in filtered_ids:
                # This node becomes a direct child of the root
                filtered_parents.append("")
            else:
                filtered_parents.append(parent)

        # Update root_id to empty string for filtered view
        # The first node (root_id) should have parent ""
        root_idx_in_filtered = (
            filtered_ids.index(root_id) if root_id in filtered_ids else 0
        )
        if root_idx_in_filtered < len(filtered_parents):
            filtered_parents[root_idx_in_filtered] = ""

        ids = filtered_ids
        labels = filtered_labels.copy()
        parents = filtered_parents
        values = filtered_values
    else:
        # Show full tree
        ids = data["ids"]
        labels = data["labels"].copy()
        parents = data["parents"]
        values = data["values"]

    # Calculate maxdepth if not provided
    if maxdepth is None:
        if clicked_node_id:
            path_cols = [
                "region",
                "country",
                "jurisdiction_level",
                "state_province",
                "city",
                "attr_type",
                "attr_value",
            ]
            maxdepth = calculate_maxdepth_for_node(clicked_node_id, path_cols)
        else:
            maxdepth = 3

    # Only update labels for the root node (the one we're drilling into)
    # When root is "world", don't modify labels (show normal view)
    # When root is a clicked node, show enhanced info for that root node
    if root_id != "world" and root_id in ids:
        idx = ids.index(root_id)
        node_depth = get_node_depth(root_id)

        # For deep nodes (attr_value level, depth >= 6), show policy list with metadata
        if node_depth >= 6 and policy_metadata_df is not None:
            # Get policy_ids_map from original data
            policy_ids = data["policy_ids_map"].get(root_id, [])
            policy_details = []

            # Get metadata for these policies
            policy_rows = policy_metadata_df[
                policy_metadata_df["policy_id"].isin(policy_ids)
            ]

            for _, policy_row in policy_rows.head(
                10
            ).iterrows():  # Limit to 10 for display
                policy_id = policy_row["policy_id"]
                # Format policy info (customize based on available columns)
                policy_info = f"{policy_id}"
                if "order_type" in policy_row and pd.notna(policy_row["order_type"]):
                    policy_info += f" ({policy_row['order_type']})"
                if "status" in policy_row and pd.notna(policy_row["status"]):
                    policy_info += f" - {policy_row['status']}"
                policy_details.append(policy_info)

            if len(policy_ids) > 10:
                policy_details.append(f"... and {len(policy_ids) - 10} more")

            # Extract original label (remove count if present)
            # Format is now: "{label}<br>({count})" so split by <br> and take first part
            original_label = labels[idx].split("<br>")[0]  # Get just the label part
            labels[idx] = (
                f"{original_label}<br>{len(policy_ids)} policies<br><br>"
                + "<br>".join(policy_details)
            )
        elif node_depth >= 4:
            # For state_province and below (but not attr_value), show policy count
            policy_list = data["policy_ids_map"].get(root_id, [])
            # Extract original label (format is "{label}<br>({count})")
            original_label = labels[idx].split("<br>")[0]
            if len(policy_list) <= 5:
                labels[idx] = (
                    f"{original_label}<br>{len(policy_list)}<br><br>Policies:<br>"
                    + "<br>".join(policy_list)
                )
            else:
                labels[idx] = (
                    f"{original_label}<br>{len(policy_list)}<br><br>{len(policy_list)} policies"
                )

    fig = go.Figure(
        go.Treemap(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            maxdepth=maxdepth,
            texttemplate="%{label}",
            textposition="middle center",
            hovertemplate="<b>%{label}</b><br>%{percentRoot:.1%} of "
            + (root_id.split("/")[-1] if root_id != "world" else "Global")
            + "<extra></extra>",
            textfont_size=16,
            marker=dict(
                colors=values,
                colorscale="Teal",  # "RdBu_r",
                showscale=True,
                line=dict(width=1, color="white"),
            ),
            tiling=dict(packing="squarify", pad=3),
        )
    )
    fig.update_layout(
        margin=dict(t=35, l=10, r=10, b=10),
    )
    return fig


# ============================================================
# USAGE IN DASH CALLBACK:
# ============================================================
# The treemap chart functions should be called from a callback that receives
# a filtered dataframe. Example:
#
# @app.callback(
#     Output('treemap', 'figure'),
#     [Input('apply-filters-btn', 'n_clicks')],
#     [State('filter-dropdown', 'value'), ...],
# )
# def update_treemap(n_clicks, filter_value, ...):
#     # Filter the dataframe based on filter inputs
#     filtered_df = filter_data(df, filter_value, ...)
#
#     # Define path columns for hierarchy
#     path_cols = [
#         "region",
#         "country",
#         "jurisdiction_level",
#         "state_province",
#         "city",
#         "attr_type",
#         "attr_value",
#     ]
#
#     # Build treemap data from filtered dataframe
#     treemap_data = build_treemap_data(df=filtered_df, path_cols=path_cols, policy_col="policy_id")
#
#     # Create and return the chart
#     fig = create_treemap_fig(treemap_data)
#     return fig
#
# For interactive click handling:
# @callback(Output('treemap', 'figure'), Input('treemap', 'clickData'), State('store', 'data'))
# def on_click(click_data, data):
#     if click_data and click_data['points'][0]['id'] in data['policy_ids_map']:
#         return create_treemap_fig(data, show_policies_for=click_data['points'][0]['id'])
#     return create_treemap_fig(data)
