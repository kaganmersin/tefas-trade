import pandas as pd
import os
import glob
from config import COMMON_EXCLUSIONS

# Directory of the script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Get my_funds from config
MY_FUNDS = COMMON_EXCLUSIONS['my_funds']

# Get all CSV files in the script's directory
csv_files = glob.glob(os.path.join(script_dir, '*.csv'))

# Create a Pandas Excel writer using XlsxWriter as the engine
output_excel_path = os.path.join(script_dir, 'output.xlsx')
with pd.ExcelWriter(output_excel_path, engine='xlsxwriter') as writer:
    all_funds_df = None  # Store the all_fund_profit_percentages_api dataframe

    for csv_file in csv_files:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file)

        # Get the base name of the CSV file and truncate it to 31 characters
        sheet_name = os.path.splitext(os.path.basename(csv_file))[0]
        sheet_name = sheet_name[:31]

        # Store the original dataframe for all_fund_profit_percentages_api
        if sheet_name == 'all_fund_profit_percentages_api':
            all_funds_df = df.copy()

        # Write the DataFrame to a specific sheet in the Excel file
        df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Get workbook and worksheet for conditional formatting
        workbook  = writer.book
        worksheet = writer.sheets[sheet_name]

        # Apply conditional formatting to all_fund_profit_percentages_api
        if sheet_name == 'all_fund_profit_percentages_api':
            # Get number of columns
            num_cols = len(df.columns)
            for col in range(2, num_cols):  # Skip Fund and Full Fund Name columns
                # Apply a conditional format to the cell range.
                worksheet.conditional_format(1, col, len(df), col, {
                    'type': '3_color_scale',
                    'min_color': "#F8696B", # Red for lowest values
                    'mid_color': "#FEE282", # Yellow for mid-range values
                    'max_color': "#73C37C"  # Green for highest values
                })

        # Apply conditional formatting to top_funds, current_funds, and my_portfolio sheets
        elif sheet_name.startswith('top_funds_') or sheet_name.startswith('current_funds_') or sheet_name.startswith('my_portfolio'):
            # Find numeric columns (exclude Fund, Full Fund Name, Appearances)
            numeric_col_indices = []
            for col_idx, col_name in enumerate(df.columns):
                if col_name not in ['Fund', 'Full Fund Name', 'Appearances'] and df[col_name].dtype in ['float64', 'int64']:
                    numeric_col_indices.append(col_idx)

            # Apply conditional formatting to numeric columns
            for col_idx in numeric_col_indices:
                worksheet.conditional_format(1, col_idx, len(df), col_idx, {
                    'type': '3_color_scale',
                    'min_color': "#F8696B", # Red for lowest values
                    'mid_color': "#FEE282", # Yellow for mid-range values
                    'max_color': "#73C37C"  # Green for highest values
                })

    # Create a new sheet with specific funds from all_fund_profit_percentages_api
    if all_funds_df is not None:
        # Filter to only include MY_FUNDS
        my_funds_df = all_funds_df[all_funds_df['Fund'].isin(MY_FUNDS)].copy()

        # Write to a new sheet
        sheet_name = 'my_funds_detailed'
        my_funds_df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Get workbook and worksheet for conditional formatting
        workbook  = writer.book
        worksheet = writer.sheets[sheet_name]

        # Apply the same conditional formatting as all_fund_profit_percentages_api
        num_cols = len(my_funds_df.columns)
        for col in range(2, num_cols):  # Skip Fund and Full Fund Name columns
            worksheet.conditional_format(1, col, len(my_funds_df), col, {
                'type': '3_color_scale',
                'min_color': "#F8696B", # Red for lowest values
                'mid_color': "#FEE282", # Yellow for mid-range values
                'max_color': "#73C37C"  # Green for highest values
            })

        print(f"Created 'my_funds_detailed' sheet with {len(my_funds_df)} funds from config.py")

print(f"All CSV files have been written to {output_excel_path}.")
