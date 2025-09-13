import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd


def create_kpi_cards(kpi_data_sources, config):
    """
    create KPI data cards
    """

    pue_df = kpi_data_sources.get("pue")
    wue_df = kpi_data_sources.get("wue")
    pue_wue_df = kpi_data_sources.get("company_name")
    energyprojections_df = kpi_data_sources.get("energy_projections_studies")

    # calculate KPIs
    all_kpis = {
        "companies_monitored": pue_wue_df["company_name"].nunique()
        if "company_name" in pue_wue_df.columns
        else 0,
        "pue_values": pue_df[pue_df['metric']=='pue']["metric_value"].dropna().count()
        if "metric_value" in pue_df.columns
        else 0,
        "wue_values": wue_df[wue_df['metric']=='wue']["metric_value"].dropna().count()
        if "metric_value" in wue_df.columns
        else 0,
        # "wue_values": df["metric_value"].dropna().count() if "metric_value" in df.columns else 0,
        "studies_assessed": energyprojections_df["citation"].nunique() if "citation" in energyprojections_df.columns else 0,
    }

    # get KPIs from the kpi_cards list in the menu_structure
    kpi_configs = config.get(
        "kpi_cards", []
    )  # kpi_configs = config.get('landing_page_cards', {}).get('kpi_cards', [])
    display_kpis = [kpi for kpi in kpi_configs if kpi.get("enabled", True)]

    cards = []

    for card_config in display_kpis:
        kpi_id = card_config.get("id")
        title = card_config.get("title")
        value = all_kpis.get(kpi_id, 0)

        # skip if KPI not calculated or title not provided
        if not title or kpi_id not in all_kpis:  # or value == 0:
            continue

        card = dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H2(
                            f"{value:,}",
                            className="text-center mb-2 kpi-value",
                            style={
                                "font-weight": "bold",
                                "color": "#2c3e50",
                            },
                        ),
                        html.P(
                            title,
                            className="text-center text-muted mb-0 kpi-title",
                        ),
                    ]
                )
            ],
            className=f"kpi-card",
        )

        cards.append(card)

    return html.Div(
        [
            dbc.Row(
                [dbc.Col(card, width=12, md=6, lg=3) for card in cards],
                className="d-flex flex-column flex-md-row align-items-center",
            )
        ],
        style={"padding": "25px", "maxWidth": "1600px", "margin": "0 auto"},
    )
