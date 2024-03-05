import pandas as pd
import glob
import os

def clean_fund_data(csv_file_path, threshold=0.35):
    # Load the CSV file
    funds_df = pd.read_csv(csv_file_path)

    # Calculate the number of NaN or 0.0 values in each row (excluding the first two columns)
    funds_df['NaN_or_Zero_Count'] = funds_df.iloc[:, 2:].apply(lambda x: (x == 0.0) | x.isna(), axis=1).sum(axis=1)

    # Total number of price columns
    total_price_columns = funds_df.shape[1] - 2  # excluding 'Fund' and 'Full Fund Name'

    # Identify funds where more than the threshold % of the prices are NaN or 0.0
    funds_to_remove = funds_df[funds_df['NaN_or_Zero_Count'] > total_price_columns * threshold]['Fund']

    # Remove these funds from the dataset
    cleaned_funds_df = funds_df[~funds_df['Fund'].isin(funds_to_remove)].drop(columns=['NaN_or_Zero_Count'])

    return cleaned_funds_df

# Define your file names and thresholds here
files_and_thresholds = [
    ('all_fund_prices-0-72.csv', 0.30),
    ('all_fund_prices-13-72.csv', 0.35),
    ('all_fund_prices-25-72.csv', 0.40),
    ('all_fund_prices-37-72.csv', 0.50),
    ('all_fund_prices-49-72.csv', 0.50),
    ('all_fund_prices-61-72.csv', 0.50),
    # Add more tuples as needed
]

# Create 'cleaned' directory if it doesn't exist
if not os.path.exists('cleaned'):
    os.makedirs('cleaned')

# Loop over the files and thresholds
for csv_file_path, threshold in files_and_thresholds:
    cleaned_data = clean_fund_data(csv_file_path, threshold)
    cleaned_data.to_csv('cleaned/cleaned_' + csv_file_path, index=False)