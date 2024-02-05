import requests
import pandas as pd
from datetime import datetime, timedelta
import os

# Function to get the previous Friday's date
def get_previous_friday(date):
    while date.weekday() != 4:  # 4 corresponds to Friday
        date -= timedelta(days=1)
    return date

# Function to fetch fund data using the TEFAS API
def fetch_fund_data(fund_code, start_date, end_date):
    url = 'https://www.tefas.gov.tr/api/DB/BindHistoryInfo'
    payload = {
        'fontip': 'YAT',
        'sfontur': '',
        'fonkod': fund_code,
        'fongrup': '',
        'bastarih': start_date.strftime('%d.%m.%Y'),
        'bittarih': end_date.strftime('%d.%m.%Y'),
        'fonturkod': '',
        'fonunvantip': ''
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data['data'])
    except requests.RequestException as e:
        print(f"API request failed: {e}")
        return pd.DataFrame()

# Function to get the price of a fund on a specific day
def get_single_day_price(date, fund_code):
    df = fetch_fund_data(fund_code, date, date)
    if not df.empty:
        price = df['FIYAT'].astype(float).iloc[0]
        price = f"{price:.3f}"
        full_fund_name = df['FONUNVAN'].iloc[0]
        return price, full_fund_name
    else:
        return None, None

# Function to validate and format price
def format_price(price):
    if price is None or price == '' or price == '0.000':
        return 'NaN'
    try:
        # Validate that the price is a float
        float_price = float(price)
        return f"{float_price:.3f}"
    except ValueError:
        return 'NaN'

# Main execution starts here
today = datetime.now()
if today.weekday() > 4:
    today = get_previous_friday(today)

# Directory of the script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Path for the fund names file
fund_names_path = os.path.join(script_dir, 'fund_names.txt')

# Read fund names from fund_names.txt
with open(fund_names_path, 'r') as file:
    all_funds = [line.strip() for line in file]

# Define the ranges for each file
ranges = [(0, 72), (13, 72), (25, 72), (37, 72), (49, 72), (61, 72)]

# Delete existing files at the start of each script execution
for start_week, end_week in ranges:
    if start_week == 0 and end_week == 72:
        file_name = 'all_fund_prices-0-72.csv'
    else:
        file_name = f'all_fund_prices-{start_week}-{end_week}.csv'
    csv_path = os.path.join(script_dir, file_name)
    if os.path.exists(csv_path):
        os.remove(csv_path)

# Process each fund
for fund in all_funds:
    try:
        print(f"Processing {fund}...")
        weekly_prices = []
        full_fund_name = ''
        for week in range(0, 73):
            date = today - timedelta(weeks=week)
            price, name = get_single_day_price(date, fund)
            if week == 0 and name:
                full_fund_name = name

            formatted_price = format_price(price)
            weekly_prices.append(formatted_price)

        # Write to each file
        for start_week, end_week in ranges:
            # Path for the CSV file
            if start_week == 0 and end_week == 72:
                file_name = 'all_fund_prices-0-72.csv'
            else:
                file_name = f'all_fund_prices-{start_week}-{end_week}.csv'
            csv_path = os.path.join(script_dir, file_name)

            # Open file for writing
            with open(csv_path, 'a') as file:
                # Write header if file is empty
                if os.stat(csv_path).st_size == 0:
                    header = 'Fund,Full Fund Name,' + ','.join([f'{(today - timedelta(weeks=week)).date()}' for week in range(start_week, end_week + 1)]) + '\n'
                    file.write(header)

                # Write data
                file.write(f"{fund},{full_fund_name}," + ','.join(weekly_prices[start_week:end_week+1]) + '\n')
                file.flush()
    except Exception as e:
        print(f"Error processing {fund}: {e}")

print("All prices have been written to their respective CSV files.")