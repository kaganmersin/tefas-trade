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

# Function to get profit info for a specific date and fund
def get_profit_info(date, fund_code):
    price, full_fund_name = get_single_day_price(date, fund_code)
    return price, full_fund_name

# Function to get the most recent price of a fund
def get_recent_price(fund_code):
    for days_back in range(3):
        date_to_check = today - timedelta(days=days_back)
        end_price, _ = get_single_day_price(date_to_check, fund_code)
        if end_price is not None:
            return end_price
    return None

# Main execution starts here
today = datetime.now() - timedelta(days=1)
if today.weekday() > 4:
    today = get_previous_friday(today)

# Directory of the script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Path for the fund names file
fund_names_path = os.path.join(script_dir, 'fund_names.txt')

# Read fund names from fund_names.txt
with open(fund_names_path, 'r') as file:
    all_funds = [line.strip() for line in file]

number_of_weeks = 74
week_dates = [today - timedelta(weeks=week) for week in range(1, number_of_weeks + 1)]
week_dates_str = [date.strftime('%Y-%m-%d') for date in week_dates]

# Paths for the CSV files
profit_csv_path = os.path.join(script_dir, 'all_fund_profit_percentages_api.csv')
price_csv_path = os.path.join(script_dir, 'all_fund_prices_api.csv')

# Open files for writing
with open(profit_csv_path, 'w') as profit_file, open(price_csv_path, 'w') as price_file:
    # Modify the header for the price CSV file to include today's date
    today_str = today.strftime('%Y-%m-%d')
    price_header = 'Fund,Full Fund Name,Start Date (' + today_str + '),' + ','.join([f'{i} Weeks ({date})' for i, date in enumerate(week_dates_str, start=1)]) + '\n'
    price_file.write(price_header)

    # Write headers
    profit_header = 'Fund,Full Fund Name,' + ','.join([f'{i} Weeks' for i in range(1, number_of_weeks + 1)]) + '\n'
    profit_file.write(profit_header)

    # Process each fund
    for fund in all_funds:
        try:
            print(f"Processing {fund}...")
            weekly_profits = []
            weekly_prices = []
            full_fund_name = ''
            # Fetch today's (or the most recent Friday's) price
            today_price = get_recent_price(fund)

            for week in range(1, number_of_weeks + 1):
                date = today - timedelta(weeks=week)
                start_price, name = get_profit_info(date, fund)
                if week == 1 and name:
                    full_fund_name = name

                if start_price is not None:
                    weekly_prices.append(start_price)
                    if today_price is not None and float(start_price) != 0:
                        profit_percentage = ((float(today_price) - float(start_price)) / float(start_price)) * 100
                        profit_percentage = f"{profit_percentage:.3f}"
                        weekly_profits.append(profit_percentage)
                    else:
                        weekly_profits.append('None')
                else:
                    weekly_profits.append('None')
                    weekly_prices.append('None')

            # Write to files with today's price included
            profit_file.write(f"{fund},{full_fund_name}," + ','.join(map(lambda x: str(x) if x != 'None' else 'None', weekly_profits)) + '\n')
            price_file.write(f"{fund},{full_fund_name},{today_price if today_price is not None else 'None'}," + ','.join(map(lambda x: str(x) if x != 'None' else 'None', weekly_prices)) + '\n')
            profit_file.flush()
            price_file.flush()
        except Exception as e:
            print(f"Error processing {fund}: {e}")

print("All profit percentages and prices have been written to their respective CSV files.")
