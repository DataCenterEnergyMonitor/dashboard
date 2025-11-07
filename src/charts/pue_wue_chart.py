import plotly.express as px
import plotly.io as pio
import pandas as pd


def create_pue_wue_scatter_plot(filtered_df, full_df=None, filters_applied=False):
    """
    Create WUE vs PUE scatter plot

    Args:
        filtered_df: DataFrame to display
        filters_applied: Boolean indicating if filters are actively applied
        full_df: unfiltered DataFrame
    """
    # Reset template to avoid Plotly template corruption bug
    pio.templates.default = "simple_white"

    company_list = full_df["company_name"].unique()
    # Define brand colors for specific companies
    brand_colors = {
        "Google": "#F4B400",  # Google Yellow
        "Microsoft": "#008AD7",  # Microsoft Gray
        "Meta (Facebook)": "#1877F2",  # Meta Blue
        "Amazon/AWS": "#FF9900",  # Amazon Orange
        "Oracle": "#C74634",  # Oracle Red
        "Dropbox": "#0061FE",  # Dropbox Blue
        "Apple": "#0088cc",  # Apple Gray
        "IBM": "#054ADA",  # IBM Blue
        "Equinix": "#FF0000",  # Equinix Red
        "Digital Realty": "#0073E6",  # Digital Realty Blue
        "OVHcloud": "#0050D7",  # OVHcloud Red
        "NVIDIA": "#76B900",  # NVIDIA Green
        "CyrusOne": "#1BD1E4",  # CyrusOne Orange
        "Alibaba": "#FF6701",  # Alibaba Orange
        "Tencent": "#0052D9",  # Tencent Blue
        "Huawei": "#FF0000",  # Huawei Red
        "NTT": "#FF0000",  # NTT Red
        "KDDI": "#FF6600",  # KDDI Orange
        "Fujitsu": "#E60012",  # Fujitsu Red
        "Hitachi": "#0066CC",  # Hitachi Blue
        "Scaleway": "#4F0599",  # Scaleway Orange
        "Yandex": "#FFCC00",  # Yandex Yellow
        "Mastercard": "#EB001B",  # Mastercard Red
        "CoreSite": "#002639",  # CoreSite Red
        "SAP": "#00B9F2",  # SAP Blue
        "Deutsche Telekom": "#E20074",  # Deutsche Telekom Magenta
        "Akamai": "#00b050",  # Akamai Green
        "Salesforce": "#1798C1",  # Salesforce Blue
        "Verizon": "#FF0000",  # Verizon Red
        "AT&T": "#067AB4",  # AT&T Blue
        "T-Systems": "#E20074",  # T-Systems Magenta
        "Taiwan Mobile": "#ff6101",
        "Baidu": "#DE0F17",  # Baidu Red
        "China Telecom": "#E60012",  # China Telecom Red
        "China Unicom": "#E60012",  # China Unicom Red
        "VISA": "#1A1F71",  # VISA Blue
    }

    palette = px.colors.qualitative.Bold

    # Assign colors: brand color if available, else from palette
    color_map = {}
    palette_idx = 0
    for company in company_list:
        if company in brand_colors:
            color_map[company] = brand_colors[company]
        else:
            color_map[company] = palette[palette_idx % len(palette)]
            palette_idx += 1

    if filtered_df.empty:
        return {
            "data": [],
            "layout": {
                "xaxis": {"title": "Power Usage Effectiveness (PUE)", "visible": True},
                "yaxis": {"title": "Water Usage Effectiveness (WUE)", "visible": True},
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
        df["metric_type"] = df["metric_type"].apply(
            lambda x: f"PUE Type: {x}<br>" if pd.notna(x) and str(x).strip() else ""
        )
        df["measurement_category"] = df["measurement_category"].apply(
            lambda x: f"PUE Measurement Category: {x}<br>"
            if pd.notna(x) and str(x).strip()
            else ""
        )
        df["time_period_category"] = df["time_period_category"].apply(
            lambda x: f"Time Period Category: {x}<br>"
            if pd.notna(x) and str(x).strip()
            else ""
        )
        df["facility_scope"] = df["facility_scope"].apply(
            lambda x: f"Facility Scope: {x}<br>"
            if pd.notna(x) and str(x).strip()
            else ""
        )
        df["region_text"] = df["region"].apply(
            lambda x: f"Region: {x}<br>" if pd.notna(x) and str(x).strip() else ""
        )
        df["country"] = df["country"].apply(
            lambda x: f"Country: {x}<br>" if pd.notna(x) and str(x).strip() else ""
        )
        df["city"] = df["city"].apply(
            lambda x: f"City: {x}<br>" if pd.notna(x) and str(x).strip() else ""
        )
        df["climate_text"] = df["assigned_climate_zones"].apply(
            lambda x: f"IECC Climate Zone: {x}<br>"
            if pd.notna(x) and str(x).strip()
            else ""
        )

    custom_data = [
        "company_name",
        "metric_type",
        "measurement_category",
        "time_period_category",
        "facility_scope",
        "region_text",
        "country",
        "city",
        "climate_text",
    ]

    filtered_df = filtered_df.copy()
    create_hover_text(filtered_df)

    # Create the scatter plot with conditional parameters
    scatter_params = {
        "data_frame": filtered_df,
        "x": "metric_value",
        "y": "wue_value",
        "labels": {
            "metric_value": "Power Usage Effectiveness (PUE)",
            "wue_value": "Water Usage Effectiveness (WUE)",
            "company_name": "Company Name",
        },
        "custom_data": custom_data,
    }

    # Only add color parameters if filters are applied
    if filters_applied:
        scatter_params["color"] = "company_name"
        scatter_params["color_discrete_map"] = color_map

    pue_wue_fig = px.scatter(**scatter_params)

    if not filters_applied:
        pue_wue_fig.update_traces(
            marker=dict(color="lightgray", size=8, opacity=0.7), showlegend=False
        )
    else:
        pue_wue_fig.update_traces(marker=dict(size=9))

        # Add background traces to foreground figure
        if full_df is not None and len(full_df) > len(filtered_df):
            # Get companies that are in the fildered data
            filtered_companies = set(filtered_df["company_name"].unique())

            # Filter background data to exclude companies already displayed
            background_df = full_df[
                ~full_df["company_name"].isin(filtered_companies)
            ].copy()

            if (
                not background_df.empty
            ):  # Only create background if there are companies to show
                create_hover_text(background_df)

                background_fig = px.scatter(
                    background_df,
                    x="metric_value",
                    y="wue_value",
                    custom_data=custom_data,
                )
                background_fig.update_traces(
                    marker=dict(color="lightgray", size=8, opacity=0.5),
                    showlegend=False,
                )

                # Add to main figure
                for trace in background_fig.data:
                    pue_wue_fig.add_trace(trace)

                # Reorder so background appears behind colored data
                pue_wue_fig.data = (
                    pue_wue_fig.data[-len(background_fig.data) :]
                    + pue_wue_fig.data[: -len(background_fig.data)]
                )

    pue_wue_fig.update_layout(
        font_family="Inter",
        plot_bgcolor="white",
        margin=dict(r=250),
        xaxis=dict(
            showgrid=False,  # disable gridlines
            dtick=0.2,  # force yearly intervals
            range=[0.8, 2.4],  # set y-axis to start at 1.0,
            showline=True,
            linecolor="black",
            linewidth=1,
            title_font=dict(size=14),
        ),
        yaxis=dict(
            range=[-0.02, filtered_df["wue_value"].max() + 0.2],
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

    # Update marker size and hover template
    pue_wue_fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"  # company name
            + "PUE: %{x}<br>"  # PUE value
            + "WUE: %{y:.2f}<br>"  # WUE value
            + "%{customdata[1]}"  # metric type (Measured or Design)
            + "%{customdata[2]}"  # measurement level (if exists)
            + "%{customdata[3]}"  # time period category
            + "%{customdata[4]}"  # facility scope
            + "%{customdata[5]}"  # Region (if exists)
            + "%{customdata[6]}"  # country (if exists)
            + "%{customdata[7]}"  # city (if exists)
            + "%{customdata[8]}"  # Climate zone (if exists)
            + "<extra></extra>"
        )
    )

    return pue_wue_fig
