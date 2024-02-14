import pandas as pd
import os
import glob

# Directory of the script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Get all CSV files in the script's directory
csv_files = glob.glob(os.path.join(script_dir, '*.csv'))

# Create a Pandas Excel writer using XlsxWriter as the engine
output_excel_path = os.path.join(script_dir, 'output.xlsx')
with pd.ExcelWriter(output_excel_path, engine='xlsxwriter') as writer:
    for csv_file in csv_files:
        # Skip files that start with 'top'
        if os.path.basename(csv_file).startswith('top'):
            continue

        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file)

        # Get the base name of the CSV file and truncate it to 31 characters
        sheet_name = os.path.splitext(os.path.basename(csv_file))[0]
        sheet_name = sheet_name[:31]

        # If the sheet name is 'all_fund_profit_percentages_api', calculate and sort by average
        if sheet_name == 'all_fund_profit_percentages_api':
            # Select only the first 14 numeric columns for mean calculation
            numeric_cols = df.select_dtypes(include=[float, int]).iloc[:, :14]
            df['Average'] = numeric_cols.mean(axis=1)

            # Sort the DataFrame based on the Average column, in descending order
            df = df.sort_values(by='Average', ascending=False)

        # Write the DataFrame to a specific sheet in the Excel file
        df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Apply conditional formatting to all_fund_profit_percentages_api
        if sheet_name == 'all_fund_profit_percentages_api':
            workbook  = writer.book
            worksheet = writer.sheets[sheet_name]

            # Get number of columns (excluding the Average column)
            num_cols = len(df.columns) - 1
            for col in range(1, num_cols + 1):  # Excel columns are 1-indexed
                # Apply a conditional format to the cell range.
                worksheet.conditional_format(1, col, len(df), col, {
                    'type': '3_color_scale',
                    'min_color': "#a60711", # Red for lowest values
                    'mid_color': "#e9f502", # Yellow for mid-range values
                    'max_color': "#096900"  # Green for highest values
                })

print(f"All CSV files have been written to {output_excel_path}.")
