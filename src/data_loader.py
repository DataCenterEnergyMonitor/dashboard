import pandas as pd
from pathlib import Path
import janitor
from janitor import clean_names

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

    dc_water_df = pd.read_excel(data_path, sheet_name='Data Center Water Use ', skiprows=1)
    dc_water_df = dc_water_df.clean_names()
    dc_water_df = dc_water_df[['company_name', 'reported_data_year']]

    # add a reporting_scope column to each DataFrame
    company_total_ec_df.loc[:, 'reporting_scope'] = 'Company Wide Electricity Use'
    dc_ec_df.loc[:, 'reporting_scope'] = 'Data Center Electricity Use'
    dc_fuel_df.loc[:, 'reporting_scope'] = 'Data Center Fuel Use'
    dc_water_df.loc[:, 'reporting_scope'] = 'Data Center Water Use'

    # combine all the dfs into one - maintaining the original columns
    reporting_df = pd.concat([company_total_ec_df, dc_ec_df, dc_fuel_df, dc_water_df], axis=0)
    reporting_df['reported_data_year'] = reporting_df['reported_data_year'].astype(int)
    
    return  reporting_df