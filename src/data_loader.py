import pandas as pd
from pathlib import Path
#import janitor
from janitor import clean_names
import re
import os
import json
import glob
from datetime import datetime



def update_metadata(excel_path, json_path="data/metadata.json"):

    mtime = os.path.getmtime(excel_path)
    last_modified = datetime.fromtimestamp(mtime).isoformat()
    
    # Get the current file's directory (src folder)
    current_dir = Path(__file__).parent
    json_path=current_dir.parent / "data" / "metadata.json"
    
    # read existing JSON or initialize
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"metadata": {}}

    data["metadata"].update({
        "source_file": os.path.basename(excel_path),
        "last_updated": last_modified
    })

    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)

def load_pue_data():
    # Get the current file's directory (src folder)
    current_dir = Path(__file__).parent
    # Go up one level and into data directory
    data_path = current_dir.parent / "data" / "DCEWM-PUEDataset.xlsx"

    pue_df = pd.read_excel(data_path, sheet_name="PUE", index_col=None)
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
    pue_df.rename(columns={'facility_scope_evident_': 'facility_scope_evident'}, inplace=True)
    pue_df.rename(columns={'geographical_scope_stated_': 'geographical_scope_stated'}, inplace=True)
    pue_df.rename(columns={'assigned_climate_zone_s_': 'assigned_climate_zones'}, inplace=True)
    pue_df.rename(columns={'default_climate_zone_s_': 'default_climate_zones'}, inplace=True)
    pue_df.rename(columns={'is_pue_self_reported_': 'self_reported'}, inplace=True)

    return pue_df


def load_wue_data():
    # Get the current file's directory (src folder)
    current_dir = Path(__file__).parent
    # Go up one level and into data directory
    data_path = current_dir.parent / "data" / "DCEWM-WUEDataset.xlsx"

    wue_df = pd.read_excel(data_path, sheet_name="WUE", index_col=None)
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
            "category_1_water_input_s_": "category_1_water_inputs",
            "facility_scope_evident_": "facility_scope_evident",
            "geographical_scope_stated_": "geographical_scope_stated",
            "assigned_climate_zone_s_": "assigned_climate_zones",
            "default_climate_zone_s_": "default_climate_zones",
            "is_wue_self_reported_": "self_reported",
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