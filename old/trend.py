from tefas import Crawler
from datetime import datetime, timedelta
import pandas as pd

# Initialize the Crawler
tefas = Crawler()

def get_previous_friday(date):
    while date.weekday() != 4:  # 4 corresponds to Friday
        date -= timedelta(days=1)
    return date

def get_single_day_price(date, fund_name):
    try:
        # Fetch the fund data for a single day
        data = tefas.fetch(start=date.strftime('%Y-%m-%d'), 
                           end=date.strftime('%Y-%m-%d'), 
                           name=fund_name, 
                           columns=['date', 'price', 'title'])
        
        df = pd.DataFrame(data)
        if df.empty:
            return None, None  # Return None if the DataFrame is empty

        price = df['price'].astype(float).iloc[0]
        # Format price with three decimal places
        price = f"{price:.3f}"
        full_fund_name = df['title'].iloc[0]  # Get the full fund name

        return price, full_fund_name
    except Exception as e:
        print(f"Could not fetch data for {date} for fund {fund_name}: {e}")
        return None, None

def get_profit_info(date, fund_name):
    # Fetch the price for the given date
    price, full_fund_name = get_single_day_price(date, fund_name)
    return price, full_fund_name

def get_recent_price(fund_name):
    # Attempt to fetch the price for today, then yesterday, and then the day before yesterday
    for days_back in range(3):  # 0 (today), 1 (yesterday), 2 (day before yesterday)
        date_to_check = today - timedelta(days=days_back)
        end_price, _ = get_single_day_price(date_to_check, fund_name)
        if end_price is not None:
            return end_price  # Return price as soon as we get a non-None value
    return None  # Return None if price is not found for all three days


# Define the end date as today and adjust if it's a weekend
today = datetime.now()
if today.weekday() > 4:  # Saturday (5) or Sunday (6)
    today = get_previous_friday(today)

# Read fund names from fund_names.txt
with open('fund_names.txt', 'r') as file:
    all_funds = [line.strip() for line in file]

number_of_weeks = 26
# Open the file for writing and update it for each fund
week_dates = [today - timedelta(weeks=week) for week in range(1, number_of_weeks + 1)]
week_dates_str = [date.strftime('%Y-%m-%d') for date in week_dates]

# Open the file for writing and update it for each fund
with open('all_fund_profit_percentages.csv', 'w') as profit_file, open('all_fund_prices.csv', 'w') as price_file:
    # Write the header for profit file
    profit_header = 'Fund,Full Fund Name,' + ','.join([f'{i} Weeks' for i in range(1, number_of_weeks + 1)]) + '\n'
    profit_file.write(profit_header)

    # Write the header for price file with dates
    price_header = 'Fund,Full Fund Name,' + ','.join([f'{i} Weeks ({date})' for i, date in enumerate(week_dates_str, start=1)]) + '\n'
    price_file.write(price_header)

    
    for fund in all_funds:
        try:
            print(f"Processing {fund}...")
            weekly_profits = []
            weekly_prices = []
            full_fund_name = ''
            for week in range(1, number_of_weeks + 1):
                # Calculate the date for each week
                date = today - timedelta(weeks=week)
                start_price, name = get_profit_info(date, fund)
                if week == 1 and name:  # Assume the full fund name doesn't change
                    full_fund_name = name
    
                if start_price is not None:
                    end_price = get_recent_price(fund)  # Fetch the most recent price available
                    print(f"Week {week}: start_price = {start_price}, end_price = {end_price}")  # Debug print
                    weekly_prices.append(start_price)  # Add start_price to weekly_prices
                    if end_price is not None and float(start_price) != 0:
                        # Calculate and format profit percentage
                        profit_percentage = ((float(end_price) - float(start_price)) / float(start_price)) * 100
                        profit_percentage = f"{profit_percentage:.3f}"
                        weekly_profits.append(profit_percentage)
                    else:
                        weekly_profits.append('None')
                else:
                    weekly_profits.append('None')
                    weekly_prices.append('None')
                    
            # Write each fund's data to the profit file and price file
            profit_file.write(f"{fund},{full_fund_name}," + ','.join(map(lambda x: str(x) if x != 'None' else 'None', weekly_profits)) + '\n')
            price_file.write(f"{fund},{full_fund_name}," + ','.join(map(lambda x: str(x) if x != 'None' else 'None', weekly_prices)) + '\n')
            profit_file.flush()  # Force flush the buffer to the profit file
            price_file.flush()  # Force flush the buffer to the price file
        except Exception as e:
            print(f"Error processing {fund}: {e}")

print("All profit percentages and prices have been written to their respective CSV files.")
