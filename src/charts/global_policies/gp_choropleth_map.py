import plotly.express as px
import numpy as np
from helpers.geojson_cache import get_geojson


def create_gp_choropleth_map(
    filtered_df, filtered_geo_df, filters_applied=False, geojson=None
):
    # 1. Background Layer
    country_geo_df = (
        filtered_df.groupby("country_iso_code")["unique_per_country"]
        .max()
        .reset_index()
    )
    country_geo_df["log_val"] = np.log10(country_geo_df["unique_per_country"])

    tick_vals = [1, 2, 5, 10, 20, 27]
    tick_text = [str(i) for i in tick_vals]
    custom_blues = [[0, "#cbd9e6"], [0.5, "#88a9c3"], [1, "#395970"]]

    fig = px.choropleth(
        country_geo_df,
        locations="country_iso_code",
        locationmode="ISO-3",
        color="log_val",
        color_continuous_scale=custom_blues,
        hover_data={"unique_per_country": True, "log_val": False},
    )

    # Update colored country borders to separate NLD/DEU
    fig.update_traces(marker_line_color="#a5b8c7", marker_line_width=0.6)

    # 2. State Outlines
    state_geo_df = filtered_df.dropna(subset=["state_iso_code"]).drop_duplicates(
        "state_iso_code"
    )

    if not state_geo_df.empty:
        # Use provided geojson or get from cache/URL
        geojson_data = geojson if geojson is not None else get_geojson()

        fig.add_choropleth(
            geojson=geojson_data,
            locations=state_geo_df["state_iso_code"],
            z=[0] * len(state_geo_df),
            featureidkey="properties.iso_3166_2",
            showscale=False,
            colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
            marker_line_color="white",
            marker_line_width=0.5,
            hoverinfo="skip",
        )

    # 3. Bubbles (Ensuring visibility and legend presence)
    state_bubbles = filtered_geo_df.dropna(
        subset=["state_lat", "state_lon", "unique_per_state"]
    ).drop_duplicates("state_iso_code")
    city_bubbles = filtered_geo_df.dropna(
        subset=["lat", "lon", "unique_per_city"]
    ).drop_duplicates(["lat", "lon"])

    if not state_bubbles.empty:
        fig.add_scattergeo(
            lat=state_bubbles["state_lat"],
            lon=state_bubbles["state_lon"],
            text=state_bubbles["state_province"],
            name="State",
            marker=dict(
                size=state_bubbles["unique_per_state"],
                color="rgba(255, 165, 0, 0.75)",
                sizemode="area",
                sizeref=2.0
                * max(filtered_df["unique_per_state"].fillna(0))
                / (25.0**2),
                line=dict(width=1, color="white"),
            ),
        )

    if not city_bubbles.empty:
        fig.add_scattergeo(
            lat=city_bubbles["lat"],
            lon=city_bubbles["lon"],
            text=city_bubbles["city"],
            name="City",
            marker=dict(
                size=city_bubbles["unique_per_city"],
                color="rgba(230, 0, 0, 0.85)",
                sizemode="area",
                sizeref=2.0 * max(filtered_df["unique_per_city"].fillna(0)) / (15.0**2),
                line=dict(width=1, color="white"),
            ),
        )

    # 4. FLAT MAP STYLING & LEGEND STACKING
    fig.update_geos(
        projection_type="equirectangular",
        showframe=False,
        showcoastlines=True,
        coastlinecolor="#708da3",
        coastlinewidth=0.8,
        showcountries=True,
        countrycolor="#a5b8c7",
        countrywidth=0.6,
        showland=True,
        landcolor="#FDFDFD",
        showocean=False,
        # Enable zooming and panning
        projection_rotation=dict(lon=0, lat=0),
    )

    fig.update_layout(
        # --- POLICIES COLOR BAR (Moved higher) ---
        coloraxis_colorbar=dict(
            title="Policy Count",
            tickvals=np.log10(tick_vals),
            ticktext=tick_text,
            len=0.4,
            yanchor="top",
            y=0.75,  # Adjusted to sit just below Jurisdiction
            x=1.02,
            thickness=15,
        ),
        # --- JURISDICTION LEGEND (Top Right) ---
        legend=dict(
            title_text="Jurisdiction",
            itemsizing="constant",
            yanchor="top",
            y=0.9,  # Kept near the top
            xanchor="left",
            x=1.02,
            bgcolor="rgba(255,255,255,0)",
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin={"r": 150, "t": 50, "l": 20, "b": 20},
        height=800,
        # Enable both zoom and pan for geo plots (users can drag to pan, use buttons to zoom)
        dragmode="pan",  # Allow panning by dragging
    )

    return fig
