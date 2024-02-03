import pandas as pd
import os
import glob

# Get all CSV files in the current directory and subdirectories
csv_files = glob.glob('**/*.csv', recursive=True)

# Create a Pandas Excel writer using XlsxWriter as the engine
with pd.ExcelWriter('output.xlsx', engine='xlsxwriter') as writer:
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

# No need to call writer.save()

print("All CSV files have been written to output.xlsx.")