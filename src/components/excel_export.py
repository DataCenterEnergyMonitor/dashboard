from pathlib import Path
import pandas as pd
from dash import dcc
import io


def create_filtered_excel_download(
    input_path: str | Path,
    output_filename: str,
    sheets_to_export: list[str] = None,
    internal_prefix: str = "_internal_",
    skip_rows: int = 0,
    n_clicks: int = None,
    new_column_names = None,
) -> dcc.Download | None:
    """
    Create a filtered Excel download removing columns with specified prefix and initial rows from selected sheets.

    Args:
        input_path (str | Path): Path to source Excel file
        output_filename (str): Name of the output Excel file
        sheets_to_export (list[str], optional): List of sheet names to export.
            If None, exports all sheets.
        internal_prefix (str, optional): Prefix for columns to exclude.
            Defaults to '_internal_'.
        skip_rows (int, optional): Number of initial rows to skip in each sheet.
            Defaults to 0.
        n_clicks (int, optional): Click count from callback.
            Defaults to None.
        new_column_names: set of columns that should be renamed upon export. Format: {"Current Name": "New Name"}

    Returns:
        dcc.Download | None: Download object or None if n_clicks is None
    """
    if n_clicks is None:
        return None

    def create_excel(output_buffer):
        # Read the original Excel file
        excel_file = pd.ExcelFile(input_path)

        # If no sheets specified, export all sheets
        if sheets_to_export is None:
            sheets_to_process = excel_file.sheet_names
        else:
            sheets_to_process = [
                sheet for sheet in sheets_to_export if sheet in excel_file.sheet_names
            ]
        
        with pd.ExcelWriter(output_buffer, engine="openpyxl") as writer:
            for sheet_name in sheets_to_process:
                # Read the sheet, skipping specified number of rows
                df = pd.read_excel(
                    excel_file, sheet_name=sheet_name, skiprows=skip_rows
                )
                if new_column_names:
                # Use the rename method to update column headers
                    df = df.rename(columns=new_column_names)

                # Filter out columns with the internal prefix
                public_columns = [
                    col for col in df.columns if not col.startswith(internal_prefix)
                ]
                filtered_df = df[public_columns]

                # Write the filtered sheet
                filtered_df.to_excel(writer, sheet_name=sheet_name, index=False)

    return dcc.send_bytes(create_excel, output_filename)
