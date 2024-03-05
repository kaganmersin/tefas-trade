import pandas as pd

def calculate_profit_percentages(file_name):
    # Read the CSV file
    df = pd.read_csv(file_name)

    # Calculate profit percentages
    oldest_price_index = -1
    for i in range(len(df.columns) - 1, 1, -1):
        if not pd.to_numeric(df.iloc[:, i], errors='coerce').isna().all():
            oldest_price_index = i
            break

    if oldest_price_index == -1:
        print(f"No valid price data found in {file_name}.")
        return

    for i in range(2, oldest_price_index):
        df.iloc[:, i] = pd.to_numeric(df.iloc[:, i], errors='coerce')
        # Calculate percentage and round to three decimal places
        df.iloc[:, i] = round((df.iloc[:, i] / df.iloc[:, oldest_price_index] - 1) * 100, 3)

    # Drop the oldest price column as we don't calculate its percentage change
    df = df.drop(df.columns[oldest_price_index], axis=1)

    # Replace NaNs with 0 (assuming no change for missing data)
    df = df.fillna(0)

    # Write to a new CSV file
    new_file_name = file_name.replace('cleaned_all_fund_prices', 'cleaned_all_fund_percentages')
    df.to_csv(new_file_name, index=False)
    print(f"Output written to {new_file_name}")

# List of your files
files = [
    'cleaned_all_fund_prices-0-72.csv',
    'cleaned_all_fund_prices-13-72.csv',
    'cleaned_all_fund_prices-25-72.csv',
    'cleaned_all_fund_prices-37-72.csv',
    'cleaned_all_fund_prices-49-72.csv',
    'cleaned_all_fund_prices-61-72.csv'
]

# Process each file
for file in files:
    calculate_profit_percentages(file)