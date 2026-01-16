import pandas as pd
from pathlib import Path
#import janitor
from janitor import clean_names
import re
import os
import json
import glob
from datetime import datetime
import numpy as np
import sys
import time

# def update_metadata(excel_path, json_path="data/metadata.json"):

#     mtime = os.path.getmtime(excel_path)
#     last_modified = datetime.fromtimestamp(mtime).isoformat()
    
#     # Get the current file's directory (src folder)
#     current_dir = Path(__file__).parent
#     json_path=current_dir.parent / "data" / "metadata.json"
    
#     # read existing JSON or initialize
#     try:
#         with open(json_path, "r") as f:
#             data = json.load(f)
#     except FileNotFoundError:
#         data = {"metadata": {}}

#     data["metadata"].update({
#         "source_file": os.path.basename(excel_path),
#         "last_updated": last_modified
#     })

#     with open(json_path, "w") as f:
#         json.dump(data, f, indent=2)

def load_pue_data():
    # Get the current file's directory (src folder)
    current_dir = Path(__file__).parent
    # Go up one level and into data directory
    data_path = current_dir.parent / "data" / "DCEWM-PUEDataset.xlsx"

    pue_df = pd.read_excel(data_path, sheet_name="PUE", index_col=None, skiprows=1)
    pue_df = pue_df.clean_names()

    # Clean string columns
    string_columns = [
        "facility_scope",
        "company_name",
        "city",
        "county",
        "country",
        "region",
        "measurement_category",
    ]
    for col in string_columns:
        if col in pue_df.columns:
            pue_df[col] = pue_df[col].str.strip()

    pue_df["metric"] = "pue"
    pue_df.rename(columns={"pue_type": "metric_type"}, inplace=True)
    pue_df.rename(columns={"pue_value": "metric_value"}, inplace=True)
    # pue_df.rename(columns={'facility_scope_evident_': 'facility_scope_evident'}, inplace=True)
    # pue_df.rename(columns={'geographical_scope_stated_': 'geographical_scope_stated'}, inplace=True)
    # pue_df.rename(columns={'assigned_climate_zone_s_': 'assigned_climate_zones'}, inplace=True)
    # pue_df.rename(columns={'default_climate_zone_s_': 'default_climate_zones'}, inplace=True)
    # pue_df.rename(columns={'is_pue_self_reported_': 'self_reported'}, inplace=True)

    return pue_df


def load_wue_data():
    # Get the current file's directory (src folder)
    current_dir = Path(__file__).parent
    # Go up one level and into data directory
    data_path = current_dir.parent / "data" / "DCEWM-WUEDataset.xlsx"

    wue_df = pd.read_excel(data_path, sheet_name="WUE", index_col=None, skiprows=1)
    wue_df = wue_df.clean_names()

    # Clean string columns
    string_columns = [
        "facility_scope",
        "company_name",
        "city",
        "county",
        "country",
        "region",
        "measurement_category",
    ]
    for col in string_columns:
        if col in wue_df.columns:
            wue_df[col] = wue_df[col].str.strip()

    wue_df["metric"] = "wue"

    # clean column names
    wue_df.rename(
        columns={
            # "category_1_water_input_s_": "category_1_water_inputs",
            # "facility_scope_evident_": "facility_scope_evident",
            # "geographical_scope_stated_": "geographical_scope_stated",
            # "assigned_climate_zone_s_": "assigned_climate_zones",
            # "default_climate_zone_s_": "default_climate_zones",
            # "is_wue_self_reported_": "self_reported",
            "wue_type": "metric_type",
            "wue_value": "metric_value"
        },
        inplace=True,
    )

    return wue_df


def create_pue_wue_data(pue_df, wue_df):
    """
    Combine PUE and WUE data into a single DataFrame.

    Args:
        pue_df: PUE dataframe
        wue_df: WUE dataframe
    """
    pue_df = pue_df.copy()
    wue_df = wue_df.copy()

    # # DEBUG: list of columns
    # print("PUE columns:", pue_df.columns.tolist())
    # print("\nWUE columns:", wue_df.columns.tolist())
    
    # print("\nClimate zones in PUE:", "assigned_climate_zones" in pue_df.columns)
    # print("Climate zones in WUE:", "assigned_climate_zones" in wue_df.columns)
    

    wue_selected = wue_df[
        [
            "company_name",
            "facility_scope",
            "verbatim_geographical_scope",
            "time_period_category",
            "time_period_value",
            "metric_value",
            "category_1_water_inputs",
        ]
    ]

    pue_wue_df = pd.merge(
        pue_df,
        wue_selected,
        on=[
            "company_name",
            "facility_scope",
            "verbatim_geographical_scope",
            "time_period_category",
            "time_period_value",
        ],
        how="left",
        suffixes=("_pue", "_wue"),
    )
    # select only the relevant columns
    pue_wue_df = pue_wue_df[
        [
            "company_name",
            "facility_scope",
            "verbatim_geographical_scope",
            "metric",
            "metric_value_pue",
            "metric_value_wue",
            "time_period_value",
            "time_period_category",
            "measurement_category",
            "region",
            "country",
            "state_province",
            "city",
            "county",
            "metric_type",
            "assigned_climate_zones",
            "default_climate_zones",
            "assigned_cooling_technologies",
            "category_1_water_inputs",
        ]
    ]

    pue_wue_df.rename(
        columns={"metric_value_pue": "metric_value", "metric_value_wue": "wue_value"},
        inplace=True,
    )

    pue_wue_df = pue_wue_df.drop_duplicates()

    # append wue_df to pue_wue_df dataframe
    pue_wue_df = pd.concat([pue_wue_df, wue_df], ignore_index=True)

    return pue_wue_df

def fill_inactive_company_years(df):
    """
    For companies marked as 'company Inactive', fill all subsequent years
    """
    all_years = sorted(df['year'].unique())
    filled_rows = []
    
    for company, company_data in df.groupby('company'):
        
        # find the rows where a company became inactive
        inactive_rows = company_data[company_data['reports_pue'] == 'company Inactive']
        
        if not inactive_rows.empty:
            # extract the metadata from the first recorded inactive year
            first_row = inactive_rows.sort_values('year').iloc[0]
            first_inactive_year = first_row['year']
            
            successor = first_row.get('successor_entity', "")
            status_date = first_row.get('status_effective_date', "")
            if status_date and hasattr(status_date, 'strftime'):
                status_date = status_date.strftime('%Y-%m-%d')
            
            # create a set of years that already have data for this company
            existing_years = set(company_data['year'])
            
            # append the rows with inactive company details following the row with the first inactive year
            for year in all_years:
                if year > first_inactive_year and year not in existing_years:
                    filled_rows.append({
                        'company': company,
                        'year': year,
                        'reports_pue': 'company Inactive',
                        'reports_wue': 'company Inactive',
                        'successor_entity': successor,
                        'status_effective_date': status_date,
                    })
    
    if filled_rows:
        return pd.concat([df, pd.DataFrame(filled_rows)], ignore_index=True)
    
    return df

# load companies list data for pue and wue reporting
def load_pue_wue_companies_data():
    # Get the current file's directory (src folder)
    current_dir = Path(__file__).parent
    # Go up one level and into data directory
    data_path = current_dir.parent / "data" / "Companies_list.xlsx"

    companies_df = pd.read_excel(data_path, sheet_name="summary", index_col=None, skiprows=1)
    companies_df = companies_df.clean_names()

    # Clean string columns
    string_columns = [
        "company",
        "entity_status",
        "successor_entity",
        "year_founded"
    ]
    for col in string_columns:
        if col in companies_df.columns:
            companies_df[col] = companies_df[col].str.strip()

    # Set NaN values in year_founded to 2000
    companies_df['year_founded'] = pd.to_numeric(companies_df['year_founded'], errors='coerce')
    companies_df['year_founded'].fillna(2000, inplace=True)
    companies_df['year_founded'] = companies_df['year_founded'].astype(int)

    # Go up one level and into data directory
    data_path = current_dir.parent / "data" / "Companies_list.xlsx"

    df = pd.read_excel(data_path, sheet_name="reporting_status", index_col=None)
    df = df.clean_names()

    # Clean string columns
    string_columns = [
        "company",
        "reports_pue",
        "reports_wue"
    ]
    for col in string_columns:
        if col in df.columns:
            df[col] = df[col].str.strip()

    # Merge the two dataframes
    pue_wue_reporting_df = pd.merge(
        df,
        companies_df,
        on="company",
        how="left"
    )

    # Keep only relevant fields
    pue_wue_reporting_df = pue_wue_reporting_df[
            [
                "company",
                "year",
                "reports_pue",
                "reports_wue",
                "year_founded",
                "entity_status",
                "successor_entity",
                "status_effective_date",
            ]
        ]

    # Set NaN values in year_founded to 2000
    pue_wue_reporting_df['year_founded'] = pd.to_numeric(pue_wue_reporting_df['year_founded'], errors='coerce')
    pue_wue_reporting_df['year_founded'].fillna(2000, inplace=True)
    pue_wue_reporting_df['year_founded'] = pue_wue_reporting_df['year_founded'].astype(int)

    # Set reporting status to Company not established if year_founded > reporting year 
    pue_wue_reporting_df.loc[pue_wue_reporting_df['year'] < pue_wue_reporting_df['year_founded'], ['reports_pue', 'reports_wue']] = 'company not established'

    # handle Pending Data status
    # current_date = datetime.today()
    # current_year = current_date.year
    # pue_wue_reporting_df.loc[
    #     (pue_wue_reporting_df['year'] == current_year) &
    #     (pue_wue_reporting_df[['entity_status']].eq(
    #         'no reporting evident').all(axis=1)), ['reports_pue', 'reports_wue']] = 'not yet released'
    cols_to_check = ['reports_pue', 'reports_wue']
    current_year = datetime.today().year

    # iterate and update each column separately
    for col in cols_to_check:
        mask = (
            (pue_wue_reporting_df['year'] == current_year) & 
            (
                pue_wue_reporting_df[col].isna() | 
                pue_wue_reporting_df[col].eq('') | 
                pue_wue_reporting_df[col].eq('no reporting evident') |
                pue_wue_reporting_df[col].eq('not yet released')
            )
        )
        
        # Apply update to this column only
        pue_wue_reporting_df.loc[mask, col] = 'pending'
    
    pue_wue_reporting_df = fill_inactive_company_years(pue_wue_reporting_df)
    pue_wue_reporting_df.rename(columns={"company": "company_name"}, inplace=True)

    return pue_wue_reporting_df


# data load for Energy Demand and Projections page
def load_energyprojections_data():
    # Get the current file's directory (src folder)
    current_dir = Path(__file__).parent
    # Go up one level and into data directory
    data_path = current_dir.parent / "data" / "DCEWM-EnergyStudiesData.xlsx"

    df = pd.read_excel(data_path, sheet_name="Data Viz", index_col=None, skiprows=4)

    # pivot longer all year columns
    year_columns = [col for col in df.columns if re.match(r"^\d{4}$", str(col))]
    df = df.melt(
        id_vars=[col for col in df.columns if col not in year_columns],
        value_vars=year_columns,
        var_name="year",
        value_name="energy_demand",
    )

    df = df.clean_names()
    df = df[df["energy_demand"] != 0]

    # Remove NaN values as well
    df = df.dropna(subset=["energy_demand"])

    # Convert year to numeric to ensure proper x-axis positioning
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    # Ensure continuity between Historical and scenario data
    # Add the last historical point as the first point of each scenario
    df_continuous = []

    for citation in df["citation"].unique():
        citation_data = df[df["citation"] == citation].copy()

        # Get historical data
        historical_data = citation_data[citation_data["label"] == "Historical"].copy()

        if not historical_data.empty:
            # Find the last historical point (excluding NaN values)
            valid_historical = historical_data[historical_data["energy_demand"].notna()]
            if not valid_historical.empty:
                last_historical = valid_historical.loc[
                    valid_historical["year"].idxmax()
                ].copy()
            else:
                continue  # Skip if no valid historical data

            # Get all scenario labels (non-Historical)
            scenario_labels = citation_data[citation_data["label"] != "Historical"][
                "label"
            ].unique()

            # Add the last historical point to each scenario
            for scenario in scenario_labels:
                scenario_data = citation_data[citation_data["label"] == scenario].copy()

                if not scenario_data.empty:
                    # Check if this year already exists in the scenario
                    if last_historical["year"] not in scenario_data["year"].values:
                        # Create a new row for continuity
                        continuity_point = last_historical.copy()
                        continuity_point["label"] = scenario

                        # Add to the scenario data
                        scenario_data = pd.concat(
                            [pd.DataFrame([continuity_point]), scenario_data],
                            ignore_index=True,
                        )
                        scenario_data = scenario_data.sort_values("year")

                df_continuous.append(scenario_data)

        # Add historical data (unchanged)
        df_continuous.append(historical_data)

        # Add any data that doesn't have Historical counterpart
        non_historical_citations = citation_data[citation_data["label"] != "Historical"]
        if historical_data.empty and not non_historical_citations.empty:
            df_continuous.append(non_historical_citations)

    # Combine all data
    if df_continuous:
        df = pd.concat(df_continuous, ignore_index=True)
        df = df.sort_values(["citation", "label", "year"])

        # DEBUG: Check PBH records specifically
        print(f"\n=== PBH DEBUG ===")
        pbh_data = df[df["citation"] == "PBH(2018)"]
        print(f"PBH total records: {len(pbh_data)}")
        if not pbh_data.empty:
            for label in pbh_data["label"].unique():
                label_data = pbh_data[pbh_data["label"] == label]
                print(f"PBH {label}: {len(label_data)} records")
                print(f"  Years: {sorted(label_data['year'].tolist())}")
                print(f"  Values: {label_data['energy_demand'].tolist()}")
        print("=== END PBH DEBUG ===\n")

    # Clean string columns
    string_columns = [
        "region",
        "data_center_types",
        "associated_granularity",
        "modeling_approaches",
        "input_data_types",
        "time_horizon",
        "projection_narrative",
        "label",
        "source",
        "units",
        "data_series_values",
        "citation",
        "year_of_publication",
        "apa_reference",
        "publishing_institution_types",
        "author_institution_types",
    ]
    for col in string_columns:
        if col in df.columns:
            df[col] = df[col].where(df[col].isna(), df[col].astype(str).str.strip())

    return df

def load_gp_data():
    # Get the current file's directory (src folder)
    current_dir = Path(__file__).parent
    # Go up one level and into data directory
    data_path = current_dir.parent / "data" / "DCEWM-GlobalPolicies.xlsx"

    df = pd.read_excel(data_path, sheet_name="Policy_Eval", index_col=None, skiprows=2)

    df = df[
        [
            "policy_id",
            "version",
            "authors",
            "offices_held",
            "date_introduced",
            "date_of_amendment",
            "date_enacted",
            "date_killed",
            "date_in_effect",
            "jurisdiction_level",
            "city",
            "county",
            "state_province",
            "country",
            "country_iso_code",
            "state_iso_code",
            "supranational_policy_area",
            "region",
            "order_type",
            "status",
            "date_of_status",
            "Measurement and Reporting",
            "Procurement standard",
            "Performance standard",
            "Research, demonstration, and development",
            "Capacity building",
            "Rate structuring",
            "Development incentives",
            "Development restrictions",
            "Other",
            "Energy",
            "Power",
            "Water",
            "Emissions",
            "Other Environemental",
            "Taxes",
            "Permits",
            "Employement",
            "Communities",
        ]
    ]

    # pivot longer all instrument and objective columns
    instrument_columns = [
            "Measurement and Reporting",
            "Procurement standard",
            "Performance standard",
            "Research, demonstration, and development",
            "Capacity building",
            "Rate structuring",
            "Development incentives",
            "Development restrictions",
            "Other",
    ]
    transposed_df = df.melt(
        id_vars=[col for col in df.columns if col not in instrument_columns],
        value_vars=instrument_columns,
        var_name="instrument",
        value_name="has_instrument",
    )

    objective_columns = [
            "Energy",
            "Power",
            "Water",
            "Emissions",
            "Other Environemental",
            "Taxes",
            "Permits",
            "Employement",
            "Communities",
    ]
    transposed_df = transposed_df.melt(
        id_vars=[col for col in transposed_df.columns if col not in objective_columns],
        value_vars=objective_columns,
        var_name="objective",
        value_name="has_objective",
    )

    clean_df = transposed_df.drop_duplicates()

    # Extract year: check if numeric year (1900-2100) first, otherwise parse as datetime
    def extract_year(date_col):
        numeric = pd.to_numeric(date_col, errors="coerce")
        year_mask = (numeric >= 1900) & (numeric <= 2100)
        result = numeric.where(year_mask)
        dt_years = pd.to_datetime(date_col, errors="coerce").dt.year
        return result.fillna(dt_years)


    # Convert to datetime: handle numeric years (1900-2100) or parse as datetime
    def to_datetime(date_col):
        numeric = pd.to_numeric(date_col, errors="coerce")
        year_mask = (numeric >= 1900) & (numeric <= 2100)
        year_dates = pd.to_datetime(numeric.astype(str), format="%Y", errors="coerce")
        dt_dates = pd.to_datetime(date_col, errors="coerce")
        return year_dates.where(year_mask).fillna(dt_dates)


    # Extract year with fallback: date_introduced -> date_enacted -> date_in_effect -> date_killed
    clean_df["year_introduced"] = extract_year(clean_df["date_introduced"])
    clean_df["year_introduced"] = clean_df["year_introduced"].fillna(extract_year(clean_df["date_enacted"]))
    clean_df["year_introduced"] = clean_df["year_introduced"].fillna(extract_year(clean_df["date_in_effect"]))
    clean_df["year_introduced"] = clean_df["year_introduced"].fillna(extract_year(clean_df["date_killed"]))

    # Convert date_introduced to datetime with same fallback logic
    clean_df["date_introduced"] = to_datetime(clean_df["date_introduced"])
    clean_df["date_introduced"] = clean_df["date_introduced"].fillna(to_datetime(clean_df["date_enacted"]))
    clean_df["date_introduced"] = clean_df["date_introduced"].fillna(to_datetime(clean_df["date_in_effect"]))
    clean_df["date_introduced"] = clean_df["date_introduced"].fillna(to_datetime(clean_df["date_killed"]))

    return clean_df

# transpose global policies data so that we get a DataFrame with one row per objective/instrument
def transpose_gp_data(df):
    """
    Preprocess dataframe for a treemap and choropleth map visualizations.

    Args:
        df: Raw DataFrame with policy data

    Returns:
        transposed_df: Processed DataFrame with one row per objective/instrument
    """
    # identify the latest amendment name for each policy
    latest_metadata = df.groupby("policy_id")["version"].last().reset_index()

    # filter original DF to only include rows matching that Policy + Amendment combo
    amendment_df = pd.merge(df, latest_metadata, on=["policy_id", "version"], how="inner")

    # create a clean Objective DataFrame
    obj_long = amendment_df[amendment_df["has_objective"] == "Yes"].copy()
    obj_long = obj_long.drop_duplicates(
        subset=[
            "policy_id",
            "jurisdiction_level",
            "city",
            "county",
            "state_province",
            "country",
            "country_iso_code",
            "state_iso_code",
            "supranational_policy_area",
            "region",
            "order_type",
            "status",
            "objective",
        ]
    )
    obj_long["attr_type"] = "Objective"
    obj_long["attr_value"] = obj_long["objective"]

    # create a clean Instrument DataFrame
    inst_long = amendment_df[amendment_df["has_instrument"] == "Yes"].copy()
    inst_long = inst_long.drop_duplicates(
        subset=[
            "policy_id",
            "jurisdiction_level",
            "city",
            "county",
            "state_province",
            "country",
            "country_iso_code",
            "state_iso_code",
            "supranational_policy_area",
            "region",
            "order_type",
            "status",
            "instrument",
        ]
    )
    inst_long["attr_type"] = "Instrument"
    inst_long["attr_value"] = inst_long["instrument"]

    # stack instrument and objective dataframes to ensure 1 row per Objective and 1 row per Instrument
    transposed_df = pd.concat([obj_long, inst_long], ignore_index=True)

    # calculate counts on the stacked data
    transposed_df["unique_per_attr"] = transposed_df.groupby(
        [
            "jurisdiction_level",
            "city",
            "county",
            "state_province",
            "country",
            "country_iso_code",
            "state_iso_code",
            "supranational_policy_area",
            "region",
            "order_type",
            "status",
            "objective",
            "attr_value",
        ],
        dropna=False,
    )["policy_id"].transform("nunique")
    transposed_df = transposed_df.drop(
        ["instrument", "has_instrument", "objective", "has_objective"], axis=1
    )
    transposed_df["deduped_policy_count"] = (~transposed_df["policy_id"].duplicated()).astype(
        int
    )

    return transposed_df

def load_energyforecast_data():
    # Get the current file's directory (src folder)
    current_dir = Path(__file__).parent
    # Go up one level and into data directory
    data_path = (
        current_dir.parent
        / "data"
        / "AI_Data_Center_Studies_CentralTable_28012025.xlsx"
    )

    forecast_df = pd.read_excel(data_path, sheet_name="Central Table", skiprows=1)
    forecast_df = forecast_df.clean_names()

    # Clean string columns
    string_columns = [
        "publisher_company",
        "annual_electricity_consumption_twh_",
        "geographic_scope",
        "author_type_s_",
        "year",
        "results_replicable_",
        "peer_reviewed_",
        "prediction_year",
    ]
    for col in string_columns:
        if col in forecast_df.columns:
            forecast_df[col] = forecast_df[col].astype(str).str.strip()

    # forecast average  values annually
    forecast_avg = forecast_df["annual_electricity_consumption_twh_"]
    return forecast_df, forecast_avg


def load_reporting_data():
    current_dir = Path(__file__).parent
    data_path = current_dir.parent / "data" / "modules.xlsx"

    # import and clean energy consumption data
    # import and clean energy consumption data
    company_total_ec_df = pd.read_excel(
        data_path, sheet_name="Company Total Electricity Use", skiprows=1
    )
    company_total_ec_df = company_total_ec_df.clean_names()
    company_total_ec_df.rename(columns={"company": "company_name"}, inplace=True)
    company_total_ec_df = company_total_ec_df[["company_name", "reported_data_year"]]
    company_total_ec_df = company_total_ec_df.dropna(
        subset=["reported_data_year"]
    )  # remove rows with no data

    dc_ec_df = pd.read_excel(
        data_path, sheet_name="Data Center Electricity Use ", skiprows=1
    )
    dc_ec_df = dc_ec_df.clean_names()
    dc_ec_df = dc_ec_df[["company_name", "reported_data_year"]]

    dc_fuel_df = pd.read_excel(
        data_path, sheet_name="Data Center Fuel Use ", skiprows=1
    )
    dc_fuel_df = dc_fuel_df.clean_names()
    dc_fuel_df = dc_fuel_df[["company_name", "reported_data_year"]]

    # dc_water_df = pd.read_excel(data_path, sheet_name='Data Center Water Use ', skiprows=1)
    # dc_water_df = dc_water_df.clean_names()
    # dc_water_df = dc_water_df[['company_name', 'reported_data_year']]

    # add a reporting_scope column to each DataFrame
    company_total_ec_df.loc[:, "reporting_scope"] = "Company Wide Electricity Use"
    dc_ec_df.loc[:, "reporting_scope"] = "Data Center Electricity Use"
    dc_fuel_df.loc[:, "reporting_scope"] = "Data Center Fuel Use"
    # dc_water_df.loc[:, 'reporting_scope'] = 'Data Center Water Use'

    # combine all the dfs into one - maintaining the original columns
    reporting_df = pd.concat([company_total_ec_df, dc_ec_df, dc_fuel_df], axis=0)
    reporting_df["reported_data_year"] = reporting_df["reported_data_year"].astype(int)

    # strip whitespace from all string columns
    for col in reporting_df.select_dtypes(include="object").columns:
        reporting_df[col] = reporting_df[col].str.strip()

    # companies report the data one year later than the current year
    current_reporting_year = datetime.now().year - 1
    previous_reporting_year = current_reporting_year - 1

    # Strip whitespace from the 'company_name' and 'reporting_scope' columns
    reporting_df["company_name"] = reporting_df["company_name"].str.strip()
    reporting_df["reporting_scope"] = reporting_df["reporting_scope"].str.strip()

    # Create a unique DataFrame with necessary columns
    unique_companies_and_scopes = (
        reporting_df[["company_name", "reporting_scope", "reported_data_year"]]
        .drop_duplicates(ignore_index=True)
        .dropna()
    )

    # Identify combinations of company_name and reporting_scope with reported_data_year == 2024
    combinations_to_remove = unique_companies_and_scopes[
        unique_companies_and_scopes["reported_data_year"] == current_reporting_year
    ][["company_name", "reporting_scope"]]

    # Filter out the combinations to remove using merge
    unique_companies_and_scopes = unique_companies_and_scopes.merge(
        combinations_to_remove,
        on=["company_name", "reporting_scope"],
        how="left",
        indicator=True,
    )
    unique_companies_and_scopes = unique_companies_and_scopes[
        unique_companies_and_scopes["_merge"] == "left_only"
    ].drop(columns="_merge")

    # Filter out the combinations of company_name and reporting_scope with reported_data_year == previous_year
    unique_companies_and_scopes = unique_companies_and_scopes[
        unique_companies_and_scopes["reported_data_year"] == previous_reporting_year
    ][["company_name", "reporting_scope"]]

    # Set the reported_data_year to the current year and add reporting_status
    unique_companies_and_scopes = unique_companies_and_scopes.assign(
        reported_data_year=current_reporting_year,
        reporting_status="Pending data submission",
    ).drop_duplicates(ignore_index=True)

    # Prepare reporting_df
    reporting_df["reporting_status"] = "Reported"

    # Replace 'Samgung' with 'Samsung' in the entire DataFrame
    reporting_df.replace("Samgung", "Samsung", inplace=True)
    reporting_df.dropna(inplace=True)

    # Add unique_companies_and_scopes to the reporting_df
    reporting_df = pd.concat(
        [reporting_df, unique_companies_and_scopes], ignore_index=True
    )
    reporting_df = (
        reporting_df[
            [
                "company_name",
                "reporting_scope",
                "reported_data_year",
                "reporting_status",
            ]
        ]
        .drop_duplicates(ignore_index=True)
        .dropna()
    )

    return reporting_df


def load_energy_use_data():
    current_dir = Path(__file__).parent
    data_path = current_dir.parent / "data" / "modules.xlsx"

    print("\nLoading energy use data...")

    # load company total electricity use data
    company_total_ec_df = pd.read_excel(
        data_path, sheet_name="Company Total Electricity Use", skiprows=1
    )
    print(f"\nInitial company total records: {len(company_total_ec_df)}")

    company_total_ec_df = company_total_ec_df.clean_names()

    # First rename, then clean
    company_total_ec_df.rename(
        columns={
            "company": "company_name",
            "reported_total_company_electricity_use_kwh_": "electricity_usage_kwh",
        },
        inplace=True,
    )

    # Clean company names
    company_total_ec_df["company_name"] = company_total_ec_df[
        "company_name"
    ].str.strip()

    company_total_ec_df = company_total_ec_df[
        ["company_name", "reported_data_year", "electricity_usage_kwh"]
    ]
    print("\nCompany total data sample:")
    print(company_total_ec_df.head())
    print(
        f"Null values in company total electricity: {company_total_ec_df['electricity_usage_kwh'].isna().sum()}"
    )

    # load data center electricity use data
    dc_ec_df = pd.read_excel(
        data_path, sheet_name="Data Center Electricity Use ", skiprows=1
    )
    print(f"\nInitial data center records: {len(dc_ec_df)}")

    dc_ec_df = dc_ec_df.clean_names()

    # First rename, then clean
    dc_ec_df.rename(
        columns={
            "company": "company_name",
            "reported_data_center_electricity_use_kwh_": "electricity_usage_kwh",
        },
        inplace=True,
    )

    # Clean company names
    dc_ec_df["company_name"] = dc_ec_df["company_name"].str.strip()

    dc_ec_df = dc_ec_df[["company_name", "reported_data_year", "electricity_usage_kwh"]]

    # Clean electricity usage values - preserve numbers that are already clean
    dc_ec_df["electricity_usage_kwh"] = dc_ec_df["electricity_usage_kwh"].apply(
        lambda x: str(x).replace("<", "").replace(",", "") if isinstance(x, str) else x
    )
    dc_ec_df["electricity_usage_kwh"] = pd.to_numeric(
        dc_ec_df["electricity_usage_kwh"], errors="coerce"
    )

    print("\nData center data sample:")
    print(dc_ec_df.head())
    print(
        f"Null values in data center electricity: {dc_ec_df['electricity_usage_kwh'].isna().sum()}"
    )

    # Group by company and year for data centers
    dc_ec_df = (
        dc_ec_df.groupby(["company_name", "reported_data_year"])[
            "electricity_usage_kwh"
        ]
        .sum()
        .reset_index()
    )

    # add a reporting_scope column to each DataFrame
    company_total_ec_df["reporting_scope"] = "Company Wide Electricity Use"
    dc_ec_df["reporting_scope"] = "Data Center Electricity Use"

    # combine all the dfs into one
    energy_use_df = pd.concat([company_total_ec_df, dc_ec_df], axis=0)
    energy_use_df["reported_data_year"] = energy_use_df["reported_data_year"].astype(
        int
    )

    print("\nFinal dataset:")
    print(f"Total records: {len(energy_use_df)}")
    print(f"Unique companies: {len(energy_use_df['company_name'].unique())}")
    print(
        f"Years range: {energy_use_df['reported_data_year'].min()} - {energy_use_df['reported_data_year'].max()}"
    )
    print(
        f"Null values in final electricity usage: {energy_use_df['electricity_usage_kwh'].isna().sum()}"
    )
    print("\nSample of final data:")
    print(energy_use_df.head())
    print(energy_use_df.columns)

    return energy_use_df


def load_company_profile_data():
    current_dir = Path(__file__).parent
    data_path = current_dir.parent / "data" / "modules.xlsx"

    print("\nLoading company profile data...")

    # load company total electricity use data
    reporting_metrics_df = pd.read_excel(
        data_path, sheet_name="Information Source Characterist", skiprows=1
    )
    print(f"\nInitial company total records: {len(reporting_metrics_df)}")

    data_path = current_dir.parent / "data" / "modules.xlsx"
    columns_to_melt = [
        "Total company electricity use reporting?",
        "Total data center fleet electricity use reporting?",
        "Individual data center electricity use reporting?",
        "Data center fuel use reporting?",
        "PUE reporting?",
        "Total company water use reporting?",
        "Total data center fleet water  use reporting?",
        "Individual data center water use reporting?",
        "WUE reporting?",
        "Total company electric power sources reporting?",
        "Data center fleet electric power sources reporting?",
        "Individual data center electric power sources reporting?",
        "Third-party standards utilization?",
        "Total company Scope 1 GHG reporting?",
        "Data center fleet Scope 1 GHG reporting?",
        "Individual data center Scope 1 GHG reporting?",
        "Total company Scope 2 GHG reporting?",
        "Data center fleet Scope 2 GHG reporting?",
        "Individual data center Scope 2 GHG reporting?",
        "Total company Scope 3 GHG reporting?",
        "Data center fleet Scope 3 GHG reporting?",
        "Individual data center Scope 3 GHG reporting?",
    ]
    columns_to_keep = [
        "Company",
        "Title",
        "Information source type",
        "File name",
        "Date released ",
        "Data year convention",
        "Fiscal year start",
        "Fiscal year end",
        "Geographical scope",
        "If partial, which locations are included?",
        "Source citation",
    ]
    # Melt the columns into rows
    reporting_metrics_df = pd.melt(
        reporting_metrics_df,
        id_vars=columns_to_keep,
        value_vars=columns_to_melt,
        var_name="metric",
        value_name="status",
    )
    # extract the year from the file name value
    reporting_metrics_df["report_year"] = reporting_metrics_df["File name"].str.extract(
        r"(?<!\d)(2\d{3})(?!\d)"
    )
    # extract the year from the title value if the report_year is NaN
    title_years = reporting_metrics_df["Title"].str.extract(r"(?<!\d)(2\d{3})(?!\d)")[0]
    # extract and flatten to Series
    reporting_metrics_df["report_year"] = reporting_metrics_df["report_year"].fillna(
        title_years
    )
    # remove trailing spaces from the company name
    reporting_metrics_df["Company"] = reporting_metrics_df["Company"].str.strip()

    reporting_metrics_df["report_year"] = pd.to_numeric(
        reporting_metrics_df["report_year"], errors="coerce"
    )

    reporting_metrics_df.dropna(subset=["report_year"], inplace=True)
    reporting_metrics_df["report_year"] = reporting_metrics_df["report_year"].astype(
        int
    )

    # get the latest report year for each company
    most_recent_years = (
        reporting_metrics_df.groupby("Company")["report_year"].max().reset_index()
    )

    # merge to get the latest metrics and values
    company_profile_df = reporting_metrics_df.merge(
        most_recent_years, on=["Company", "report_year"]
    )

    company_profile_df = company_profile_df.clean_names()
    # company_profile_df.rename(
    #     columns={"company": "company_name"},
    #     inplace=True,
    # )
    company_profile_df = company_profile_df[["company", "metric", "status"]]
    print("\nSample of final company_profile data:")
    print(company_profile_df.head())
    print(company_profile_df.columns)

    return company_profile_df

def update_metadata():
    """Locate excel files and update metadata.json."""

    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / "data"
    json_path = data_dir / "metadata.json"

    # Ensure the data folder exists
    data_dir.mkdir(exist_ok=True)

        # load existing metadata or initialize if missing
    try:
        with open(json_path, "r") as f:
            metadata = json.load(f)
    except FileNotFoundError:
        metadata = {"files": [], "last_updated": None}

    # convert list of files to dict for easy lookup
    files_dict = {f["source_file"]: f for f in metadata.get("files", [])}

    # retrieve last modified time stamp for each excel file in data_dir
    for path in glob.glob(os.path.join(data_dir, "*.xlsx")):
        fname = os.path.basename(path)
        if fname.startswith("~$"):
            continue  # skip temporary Excel files

        mtime = datetime.fromtimestamp(os.path.getmtime(path)).isoformat()

        if fname in files_dict:
            # update if modified time changed
            if files_dict[fname]["last_modified"] != mtime:
                files_dict[fname]["last_modified"] = mtime
        else:
            # add new file entry
            files_dict[fname] = {"source_file": fname, "last_modified": mtime}

    metadata["files"] = list(files_dict.values())

    # calculate most recent modification time across all files
    metadata["last_updated"] = (
        max(f["last_modified"] for f in metadata["files"])
        if metadata["files"]
        else None
    )

    # write to json
    with open(json_path, "w") as f:
        json.dump(metadata, f, indent=2)