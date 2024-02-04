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

        # Write the DataFrame to a specific sheet in the Excel file
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"All CSV files have been written to {output_excel_path}.")
