import pandas as pd
import numpy as np

def calculate_percentages(file_path):
    # Read the CSV file and specify '' as a NaN value
    df = pd.read_csv(file_path, na_values=[''])

    # Perform your calculations here...

    # Identify columns with price data (excluding 'Fund' and 'Full Fund Name')
    price_columns = df.columns[2:]

    # Replace empty values with np.nan
    df.replace('', np.nan, inplace=True)

    # Initialize columns for percentage calculations
    for i in range(1, len(price_columns)):
        df[f'{i} Weeks'] = np.nan

    # Perform percentage calculations
    for i, col in enumerate(price_columns[1:], start=1):
        # Calculate percentages only for rows where both current and previous prices are not NaN
        valid_rows = df[price_columns[0]].notna() & df[col].notna()
        df.loc[valid_rows, f'{i} Weeks'] = ((df.loc[valid_rows, price_columns[0]].astype(float) / df.loc[valid_rows, col].astype(float) - 1) * 100).round(3)

    # Replace any remaining empty strings with np.nan
    df.replace('', np.nan, inplace=True)

    # Rearrange columns to match the desired format
    percentage_columns = [f'{i} Weeks' for i in range(1, len(price_columns))]
    df = df[['Fund', 'Full Fund Name'] + percentage_columns]

    # Save to a new CSV file
    new_file_path = file_path.replace('prices', 'percentages')
    df.to_csv(new_file_path, index=False, na_rep='NaN')
    print(f"Processed: {new_file_path}")

# List of file names
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
    calculate_percentages(file)