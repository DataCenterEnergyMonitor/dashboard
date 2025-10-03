import plotly.express as px
import pandas as pd
import hashlib


def create_pue_scatter_plot(filtered_df, full_df=None, filters_applied=False):
    """
    Create PUE scatter plot

    Args:
        filtered_df: DataFrame to display
        filters_applied: Boolean indicating if filters are actively applied
        full_df: unfiltered DataFrame
    """
    # Define years and set progressive gaps along the timeline
    # Use full dataset to ensure all years are included for consistent x-axis
    years = sorted(full_df["time_period_value"].unique())
    gap_small = 1.0
    gap_medium = 1.7
    gap_large = 2.5
    year_x_map = {}
    current_x = years[0]
    for year in years:
        year_x_map[year] = current_x
        if year < 2017:
            current_x += gap_small
        elif year < 2020:
            current_x += gap_medium
        else:
            current_x += gap_large

    # Calculate progressive jitter amount for each year (e.g., more jitter for later years)
    min_jitter = 0.3
    max_jitter = 1.1
    year_jitter_map = {}
    for i, year in enumerate(years):
        # Linear interpolation between min_jitter and max_jitter
        year_jitter_map[year] = min_jitter + (max_jitter - min_jitter) * (
            i / (len(years) - 1)
        )

    # Create deterministic jitter based on company name and year
    def add_deterministic_x_jitter(row):
        """Create deterministic x-jitter with more variation for same company/year"""
        jitter_amt = year_jitter_map[row["time_period_value"]]
        
        # Create hash from company name, year, facility scope, region and city

        hash_input = f"{row['company_name']}_{row['time_period_value']}_{row.get('facility_scope', '')}_{row.get('region', '')}_{row.get('city', '')}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
    
        # Normalize hash to [-1, 1] range
        normalized_hash = (hash_value / (16**8 - 1)) * 2 - 1
    
        # Apply jitter
        return year_x_map[row["time_period_value"]] + normalized_hash * jitter_amt

    # Apply deterministic jitter
    full_df["custom_x_jitter"] = full_df.apply(add_deterministic_x_jitter, axis=1)
    filtered_df["custom_x_jitter"] = filtered_df.apply(
        add_deterministic_x_jitter, axis=1
    )

    # Sort by company name for consistent ordering
    full_df = full_df.sort_values("company_name").copy()
    filtered_df = filtered_df.sort_values("company_name").copy()

    # Calculate y-axis range to avoid extra empty space
    ymin = max(1, filtered_df["metric_value"].min() - 0.05)
    ymax = filtered_df["metric_value"].max() + 0.05

    # Calculate x-axis range to avoid extra empty space
    xmin = filtered_df["custom_x_jitter"].min()
    xmax = full_df["custom_x_jitter"].max()

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
                "xaxis": {"title": "Time Period", "visible": True},
                "yaxis": {"title": "Power Usage Effectiveness (PUE)", "visible": True},
                "showlegend": False,
                "annotations": [
                    {
                        "text": "No data available for selected filters",
                        "xref": "paper",
                        "yref": "paper",
                        "x": 0.5,
                        "y": 0.5,
                        "showarrow": False,
                        "font": {"size": 14, "color": "gray"},
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
            lambda x: f"Measurement Category: {x}<br>"
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
        'company_name', 
        "metric_value",
        'metric_type',
        'measurement_category',
        'time_period_category',
        "time_period_value",
        'facility_scope',
        'region_text',
        'country',
        'city',
        'climate_text'
    ]

    filtered_df = filtered_df.copy()
    create_hover_text(filtered_df)

    # Create the scatter plot
    pue_fig = px.scatter(
        filtered_df,
        x="custom_x_jitter",
        y="metric_value",
        color="company_name" if filters_applied else None,
        color_discrete_map=color_map,
        labels={
            "custom_x_jitter": "Time Period",
            "metric_value": "Power Usage Effectiveness (PUE)",
            "company_name": "Company Name",
        },
        custom_data=custom_data,
        # width=1200,
        # height=700,
    )

    if not filters_applied:
        pue_fig.update_traces(
            marker=dict(color="lightgray", size=8, opacity=0.7), showlegend=False
        )
    else:
        pue_fig.update_traces(
            marker=dict(size=9, opacity=0.7, line=dict(width=0.5, color="grey")),
        )

        # Add background traces to foreground figure
        if full_df is not None and len(full_df) > len(filtered_df):
            # Get companies that are in the filtered data
            filtered_companies = set(filtered_df["company_name"].unique())

            # Filter background data to exclude companies already displayed
            background_df = full_df[
                ~full_df["company_name"].isin(filtered_companies)
            ].copy()

            if (
                not background_df.empty
            ):  # Only create background if there are companies to show
                create_hover_text(background_df)

                for company in background_df["company_name"].unique():
                    company_data = background_df[background_df["company_name"] == company]
                    
                    # Create a single gray trace for each company's background data
                    # Extract custom data values for each row with the same structure as custom_data
                    customdata_list = company_data[custom_data].values.tolist()
                    
                    # Create a single gray trace for each company's background data
                    background_trace = {
                        'type': 'scatter',
                        'mode': 'markers',
                        'x': company_data["custom_x_jitter"].tolist(),
                        'y': company_data["metric_value"].tolist(),
                        'customdata': customdata_list,
                        'marker': {
                            'color': 'lightgray',
                            'size': 7,
                            'opacity': 0.5
                        },
                        'showlegend': False,
                        'hovertemplate': (
                            "<b>%{customdata[0]}</b><br>"
                            + "PUE: %{customdata[1]}<br>"
                            + "%{customdata[2]}"
                            + "%{customdata[3]}"
                            + "%{customdata[4]}"
                            + "Time Period: %{customdata[5]}<br>"
                            + "%{customdata[6]}"
                            + "%{customdata[7]}"
                            + "%{customdata[8]}"
                            + "%{customdata[9]}"
                            + "%{customdata[10]}"
                            + '<extra></extra>'
                        ),
                        'name': company  # for debugging
                    }
                    
                    # Ensure all gray traces are added before colored traces
                    pue_fig.add_trace(background_trace, row=1, col=1)
                    
                # manually reorder: move all colored traces to the front
                num_colored = len(pue_fig.data) - len(background_df["company_name"].unique())
                num_gray = len(background_df["company_name"].unique())
                
                # Extract traces
                all_traces = list(pue_fig.data)
                colored_traces = all_traces[:num_colored]
                gray_traces = all_traces[num_colored:]
                
                # Reorder traces to render gray at the back, colored in front
                pue_fig.data = tuple(gray_traces + colored_traces)

    #xvals = [year_x_map[year] for year in years]
    pue_fig.update_xaxes(
        range=[xmin - 1, xmax + 1],
        tickvals=[year_x_map[year] for year in years],
        ticktext=[str(year) for year in years],
        showgrid=False,
        showline=True,
        linecolor="black",
        linewidth=1,
        title_font=dict(size=14),
    )
    pue_fig.update_layout(
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
            showgrid=False,  # Disable gridlines
            range=[ymin, ymax],
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
            # itemsizing="constant",
        ),
        showlegend=filters_applied,
        template="simple_white",
    )

    # Update marker size and hover template
    pue_fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"  # company name
            + "PUE: %{customdata[1]}<br>"  # PUE value
            + "%{customdata[2]}"  # metric type (Measured or Design)
            + "%{customdata[3]}"  # measurement level (if exists)
            + "%{customdata[4]}"  # time period category
            + "Time Period: %{customdata[5]}<br>"  # Time period value
            + "%{customdata[6]}"  # facility scope
            + "%{customdata[7]}"  # Region (if exists)
            + "%{customdata[8]}"  # country (if exists)
            + "%{customdata[9]}"  # city (if exists)
            + "%{customdata[10]}"  # Climate zone (if exists)
            + '<extra></extra>'
        )
    )
    return pue_fig
