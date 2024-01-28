from tefas import Crawler
from datetime import datetime, timedelta
import pandas as pd

# Initialize the Crawler
tefas = Crawler()

def get_previous_friday(date):
    while date.weekday() != 4:  # 4 corresponds to Friday
        date -= timedelta(days=1)
    return date

def get_profit_info(start_date, end_date, fund_name):
    try:
        # Fetch the fund data including the title (full fund name)
        data = tefas.fetch(start=start_date.strftime('%Y-%m-%d'), 
                           end=end_date.strftime('%Y-%m-%d'), 
                           name=fund_name, 
                           columns=['date', 'price', 'title'])  # Assuming 'title' is the correct column name
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df.sort_values(by='date', inplace=True)
        df['price'] = df['price'].astype(float)

        start_price = df['price'].iloc[0]
        end_price = df['price'].iloc[-1]

        if start_price == 0:
            return None, None  # Avoid division by zero

        profit_percentage = ((end_price - start_price) / start_price) * 100
        full_fund_name = df['title'].iloc[0]  # Get the full fund name
        
        return profit_percentage, full_fund_name
    except Exception as e:
        print(f"Could not fetch data for fund {fund_name}: {e}")
        return None, None  # Return None if there's an error

# Define the end date as today and adjust if it's a weekend
today = datetime.now()
if today.weekday() > 4:  # Saturday (5) or Sunday (6)
    today = get_previous_friday(today)

# Read fund names from fund_names.txt
with open('fund_names.txt', 'r') as file:
    all_funds = [line.strip() for line in file]

number_of_week = 15
# Open the file for writing and update it for each fund
with open('all_fund_profit_percentages.csv', 'w') as file:
    # Write the header
    header = 'Fund,Full Fund Name,' + ','.join([f'{i} Weeks' for i in range(1, number_of_week)]) + '\n'
    file.write(header)

    for fund in all_funds:
        try:
            print(f"Processing {fund}...")
            weekly_profits = []
            full_fund_name = ''
            for week in range(1, number_of_week):
                profit, name = get_profit_info(today - timedelta(weeks=week), today, fund)
                if week == 1:  # Assume the full fund name doesn't change
                    full_fund_name = name
                weekly_profits.append(profit)
            
            # Write each fund's data to the file
            file.write(f"{fund},{full_fund_name}," + ','.join(map(str, weekly_profits)) + '\n')
            file.flush()  # Force flush the buffer to the file
        except Exception as e:
            print(f"Error processing {fund}: {e}")

print("All profit percentages have been written to all_fund_profit_percentages.csv")