import pandas as pd
from pathlib import Path
import janitor
from janitor import clean_names
import datetime

def load_pue_data():
    # Get the current file's directory (src folder)
    current_dir = Path(__file__).parent
    # Go up one level and into data directory
    data_path = current_dir.parent / 'data' / 'dc_energy_use_pue.xlsx'
    
    pue_df = pd.read_excel(data_path, sheet_name='Input - PUE', skiprows=1)
    pue_df = pue_df.clean_names()
    
    # Clean string columns
    string_columns = ['facility_scope', 'company', 'geographical_scope', 'pue_measurement_level']
    for col in string_columns:
        if col in pue_df.columns:
            pue_df[col] = pue_df[col].str.strip()
    
    # Get companies with the most single locations
    company_counts = (
        pue_df[pue_df['facility_scope'] == 'Single location']
        .groupby('company')
        .size()
        .sort_values(ascending=False)
        .head(5)
        .index
        .tolist()
    )
    
     # Industry average PUE values annually
    pue_industry_avg = (
        pue_df.groupby('applicable_year')['real_pue']
        .mean()
        .reset_index()
    )
    
    return pue_df, company_counts, pue_industry_avg

def load_wue_data():
    current_dir = Path(__file__).parent
    data_path = current_dir.parent / 'data' / 'dc_energy_use_pue.xlsx'
    
    wue_df = pd.read_excel(data_path, sheet_name='Input - WUE', skiprows=1)
    wue_df = wue_df.clean_names()
    
    # set WUE industry average to 1.8 value
    wue_industry_avg = pd.DataFrame({
        'applicable_year': wue_df['applicable_year'], # The list of years from the DataFrame
        'wue': [1.8] * len(wue_df['applicable_year']) # The same WUE value for all years
    })

    # Clean string columns
    string_columns = ['facility_scope', 'company', 'geographical_scope']
    for col in string_columns:
        if col in wue_df.columns:
            wue_df[col] = wue_df[col].str.strip()
    
    # Get all unique companies
    wue_company_counts = wue_df['company'].unique().tolist()
    
    return wue_df, wue_company_counts, wue_industry_avg

def load_energyforecast_data():
    # Get the current file's directory (src folder)
    current_dir = Path(__file__).parent
    # Go up one level and into data directory
    data_path = current_dir.parent / 'data' / 'AI_Data_Center_Studies_CentralTable_28012025.xlsx'
    
    forecast_df = pd.read_excel(data_path,
                                sheet_name='Central Table',
                                skiprows=1)
    forecast_df = forecast_df.clean_names()
    
    # Clean string columns
    string_columns =['publisher_company',
                'annual_electricity_consumption_twh_',
                     'geographic_scope',
                     'author_type_s_',
                     'year',
                     'results_replicable_',
                     'peer_reviewed_',
                     'prediction_year']
    for col in string_columns:
        if col in forecast_df.columns:
            forecast_df[col] =forecast_df[col].astype(str).str.strip()
     
    # forecast average  values annually
    forecast_avg = (forecast_df['annual_electricity_consumption_twh_']
    )
    return forecast_df, forecast_avg


def load_reporting_data():
    current_dir = Path(__file__).parent
    data_path = current_dir.parent / 'data' / 'modules.xlsx'
    
    # import and clean energy consumption data
    # import and clean energy consumption data
    company_total_ec_df = pd.read_excel(data_path, sheet_name='Company Total Electricity Use', skiprows=1)
    company_total_ec_df = company_total_ec_df.clean_names()
    company_total_ec_df.rename(columns={'company': 'company_name'}, inplace=True)
    company_total_ec_df = company_total_ec_df[['company_name', 'reported_data_year']]
    company_total_ec_df = company_total_ec_df.dropna(subset=['reported_data_year']) # remove rows with no data

    dc_ec_df = pd.read_excel(data_path, sheet_name='Data Center Electricity Use ', skiprows=1)
    dc_ec_df = dc_ec_df.clean_names()
    dc_ec_df = dc_ec_df[['company_name', 'reported_data_year']]

    dc_fuel_df = pd.read_excel(data_path, sheet_name='Data Center Fuel Use ', skiprows=1)
    dc_fuel_df = dc_fuel_df.clean_names()
    dc_fuel_df = dc_fuel_df[['company_name', 'reported_data_year']]

    # dc_water_df = pd.read_excel(data_path, sheet_name='Data Center Water Use ', skiprows=1)
    # dc_water_df = dc_water_df.clean_names()
    # dc_water_df = dc_water_df[['company_name', 'reported_data_year']]

    # add a reporting_scope column to each DataFrame
    company_total_ec_df.loc[:, 'reporting_scope'] = 'Company Wide Electricity Use'
    dc_ec_df.loc[:, 'reporting_scope'] = 'Data Center Electricity Use'
    dc_fuel_df.loc[:, 'reporting_scope'] = 'Data Center Fuel Use'
    # dc_water_df.loc[:, 'reporting_scope'] = 'Data Center Water Use'

    # combine all the dfs into one - maintaining the original columns
    reporting_df = pd.concat([company_total_ec_df, dc_ec_df, dc_fuel_df], axis=0)
    reporting_df['reported_data_year'] = reporting_df['reported_data_year'].astype(int)

    # strip whitespace from all string columns
    for col in reporting_df.select_dtypes(include='object').columns:
        reporting_df[col] = reporting_df[col].str.strip()


    # companies report the data one year later than the current year
    current_reporting_year = datetime.datetime.now().year - 1
    previous_reporting_year = current_reporting_year - 1

    # Strip whitespace from the 'company_name' and 'reporting_scope' columns
    reporting_df['company_name'] = reporting_df['company_name'].str.strip()
    reporting_df['reporting_scope'] = reporting_df['reporting_scope'].str.strip()

    # Create a unique DataFrame with necessary columns
    unique_companies_and_scopes = reporting_df[['company_name', 'reporting_scope', 'reported_data_year']].drop_duplicates(ignore_index=True).dropna()

    # Identify combinations of company_name and reporting_scope with reported_data_year == 2024
    combinations_to_remove = unique_companies_and_scopes[unique_companies_and_scopes['reported_data_year'] == current_reporting_year][['company_name', 'reporting_scope']]

    # Filter out the combinations to remove using merge
    unique_companies_and_scopes = unique_companies_and_scopes.merge(combinations_to_remove, on=['company_name', 'reporting_scope'], how='left', indicator=True)
    unique_companies_and_scopes = unique_companies_and_scopes[unique_companies_and_scopes['_merge'] == 'left_only'].drop(columns='_merge')

    # Filter out the combinations of company_name and reporting_scope with reported_data_year == previous_year
    unique_companies_and_scopes = unique_companies_and_scopes[unique_companies_and_scopes['reported_data_year'] == previous_reporting_year][['company_name', 'reporting_scope']]

    # Set the reported_data_year to the current year and add reporting_status
    unique_companies_and_scopes = unique_companies_and_scopes.assign(
        reported_data_year=  current_reporting_year,
        reporting_status='Pending data submission'
    ).drop_duplicates(ignore_index=True)

    # Prepare reporting_df
    reporting_df['reporting_status'] = 'Reported'

    # Replace 'Samgung' with 'Samsung' in the entire DataFrame
    reporting_df.replace('Samgung', 'Samsung', inplace=True)
    reporting_df.dropna(inplace=True)

    # Add unique_companies_and_scopes to the reporting_df
    reporting_df = pd.concat([reporting_df, unique_companies_and_scopes], ignore_index=True)
    reporting_df = reporting_df[['company_name', 'reporting_scope', 'reported_data_year','reporting_status']].drop_duplicates(ignore_index=True).dropna()
        
    return  reporting_df



def load_energy_use_data():
    current_dir = Path(__file__).parent
    data_path = current_dir.parent / 'data' / 'modules.xlsx'

    print("\nLoading energy use data...")
    
    # load company total electricity use data
    company_total_ec_df = pd.read_excel(data_path, sheet_name='Company Total Electricity Use', skiprows=1)
    print(f"\nInitial company total records: {len(company_total_ec_df)}")
    
    company_total_ec_df = company_total_ec_df.clean_names()
    
    # First rename, then clean
    company_total_ec_df.rename(columns={
        'company': 'company_name',
        'reported_total_company_electricity_use_kwh_': 'electricity_usage_kwh'
    }, inplace=True)
    
    # Clean company names
    company_total_ec_df['company_name'] = company_total_ec_df['company_name'].str.strip()
    
    company_total_ec_df = company_total_ec_df[['company_name', 'reported_data_year', 'electricity_usage_kwh']]
    print("\nCompany total data sample:")
    print(company_total_ec_df.head())
    print(f"Null values in company total electricity: {company_total_ec_df['electricity_usage_kwh'].isna().sum()}")

    # load data center electricity use data
    dc_ec_df = pd.read_excel(data_path, sheet_name='Data Center Electricity Use ', skiprows=1)
    print(f"\nInitial data center records: {len(dc_ec_df)}")
    
    dc_ec_df = dc_ec_df.clean_names()
    
    # First rename, then clean
    dc_ec_df.rename(columns={
        'company': 'company_name',
        'reported_data_center_electricity_use_kwh_': 'electricity_usage_kwh'
    }, inplace=True)
    
    # Clean company names
    dc_ec_df['company_name'] = dc_ec_df['company_name'].str.strip()
    
    dc_ec_df = dc_ec_df[['company_name', 'reported_data_year', 'electricity_usage_kwh']]
    
    # Clean electricity usage values - preserve numbers that are already clean
    dc_ec_df['electricity_usage_kwh'] = dc_ec_df['electricity_usage_kwh'].apply(
        lambda x: str(x).replace('<', '').replace(',', '') if isinstance(x, str) else x
    )
    dc_ec_df['electricity_usage_kwh'] = pd.to_numeric(dc_ec_df['electricity_usage_kwh'], errors='coerce')
    
    print("\nData center data sample:")
    print(dc_ec_df.head())
    print(f"Null values in data center electricity: {dc_ec_df['electricity_usage_kwh'].isna().sum()}")

    # Group by company and year for data centers
    dc_ec_df = dc_ec_df.groupby(['company_name', 'reported_data_year'])['electricity_usage_kwh'].sum().reset_index()

    # add a reporting_scope column to each DataFrame
    company_total_ec_df['reporting_scope'] = 'Company Wide Electricity Use'
    dc_ec_df['reporting_scope'] = 'Data Center Electricity Use'

    # combine all the dfs into one
    energy_use_df = pd.concat([company_total_ec_df, dc_ec_df], axis=0)
    energy_use_df['reported_data_year'] = energy_use_df['reported_data_year'].astype(int)
    
    print("\nFinal dataset:")
    print(f"Total records: {len(energy_use_df)}")
    print(f"Unique companies: {len(energy_use_df['company_name'].unique())}")
    print(f"Years range: {energy_use_df['reported_data_year'].min()} - {energy_use_df['reported_data_year'].max()}")
    print(f"Null values in final electricity usage: {energy_use_df['electricity_usage_kwh'].isna().sum()}")
    print("\nSample of final data:")
    print(energy_use_df.head())
    
    return energy_use_df