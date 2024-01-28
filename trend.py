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
        full_fund_name = df['title'].iloc[0]  # Get the full fund name

        return price, full_fund_name
    except Exception as e:
        print(f"Could not fetch data for {date} for fund {fund_name}: {e}")
        return None, None

def get_profit_info(date, fund_name):
    # Fetch the price for the given date
    price, full_fund_name = get_single_day_price(date, fund_name)
    return price, full_fund_name

# Define the end date as today and adjust if it's a weekend
today = datetime.now()
if today.weekday() > 4:  # Saturday (5) or Sunday (6)
    today = get_previous_friday(today)

# Read fund names from fund_names.txt
with open('fund_names.txt', 'r') as file:
    all_funds = [line.strip() for line in file]

number_of_weeks = 24
# Open the file for writing and update it for each fund
with open('all_fund_profit_percentages.csv', 'w') as file:
    # Write the header
    header = 'Fund,Full Fund Name,' + ','.join([f'{i} Weeks' for i in range(1, number_of_weeks + 1)]) + '\n'
    file.write(header)

    for fund in all_funds:
        try:
            print(f"Processing {fund}...")
            weekly_profits = []
            full_fund_name = ''
            for week in range(1, number_of_weeks + 1):
                # Calculate the date for each week
                date = today - timedelta(weeks=week)
                start_price, name = get_profit_info(date, fund)
                if week == 1 and name:  # Assume the full fund name doesn't change
                    full_fund_name = name
                if start_price is not None:
                    end_price, _ = get_profit_info(today, fund)
                    if end_price is not None and start_price != 0:
                        profit_percentage = ((end_price - start_price) / start_price) * 100
                        weekly_profits.append(profit_percentage)
                    else:
                        weekly_profits.append('None')
                else:
                    weekly_profits.append('None')
            
            # Write each fund's data to the file
            file.write(f"{fund},{full_fund_name}," + ','.join(map(lambda x: str(x) if x != 'None' else 'None', weekly_profits)) + '\n')
            file.flush()  # Force flush the buffer to the file
        except Exception as e:
            print(f"Error processing {fund}: {e}")

print("All profit percentages have been written to all_fund_profit_percentages.csv")