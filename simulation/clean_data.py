import pandas as pd
import numpy as np

def replace_values_with_nan(file_name):
    # Read the CSV file without specifying na_values
    df = pd.read_csv(file_name)

    # Iterate over the DataFrame, replacing empty or whitespace-only cells with np.nan
    for col in df.columns:
        df[col] = df[col].apply(lambda x: np.nan if isinstance(x, str) and x.strip() == '' else x)

    # Additionally replace '0.0' as a string and 0.0 as a float with np.nan
    df.replace(['0.0', 0.0], np.nan, inplace=True)

    # Write the modified DataFrame back to the file
    df.to_csv("cleaned_" + file_name, index=False)

# List of your files
files = [
    'all_fund_prices-0-72.csv',
    'all_fund_prices-13-72.csv',
    'all_fund_prices-25-72.csv',
    'all_fund_prices-37-72.csv',
    'all_fund_prices-49-72.csv',
    'all_fund_prices-61-72.csv'
]

# Process each file
for file in files:
    replace_values_with_nan(file)
