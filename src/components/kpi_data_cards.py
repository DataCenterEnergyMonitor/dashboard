import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd


def create_kpi_cards(df, config):
    """
    create KPI data cards
    """

    # calculate KPIs
    all_kpis = {
        "companies_monitored": df["company_name"].nunique()
        if "company_name" in df.columns
        else 0,
        "pue_values": df[df['metric']=='pue']["metric_value"].dropna().count(),
        "wue_values": df[df['metric']=='wue']["metric_value"].dropna().count()
        if "metric_value" in df.columns
        else 0,
        # "wue_values": df["metric_value"].dropna().count() if "metric_value" in df.columns else 0,
        "studies_assessed": df["study_id"].nunique() if "study_id" in df.columns else 0,
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
