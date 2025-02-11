import pandas as pd
from pathlib import Path
import janitor

def load_pue_data():
    # Get the current file's directory (src folder)
    current_dir = Path(__file__).parent
    # Go up one level and into data directory
    data_path = current_dir.parent / 'data' / 'dc_energy_use_pue.xlsx'
    
    pue_df = pd.read_excel(data_path, sheet_name='Input - PUE', skiprows=1)
    pue_df = pue_df.clean_names()
    company_counts = pue_df["company"].value_counts().head(5).index.tolist()
    
    # Industry average PUE values annually
    pue_industry_avg = pue_df.groupby('applicable_year')['real_pue'].mean().reset_index()
    
    return pue_df, company_counts, pue_industry_avg

def load_wue_data():
    current_dir = Path(__file__).parent
    data_path = current_dir.parent / 'data' / 'dc_energy_use_pue.xlsx'
    
    wue_df = pd.read_excel(data_path, sheet_name='Input - WUE', skiprows=1)
    wue_df = wue_df.clean_names()
    wue_company_counts = wue_df["company"].value_counts().head(5).index.tolist()
    
    # set WUE industry average to 1.8 value
    wue_industry_avg = pd.DataFrame({
        'applicable_year': wue_df['applicable_year'], # The list of years from the DataFrame
        'wue': [1.8] * len(wue_df['applicable_year']) # The same WUE value for all years
    })
    
    return wue_df, wue_company_counts, wue_industry_avg