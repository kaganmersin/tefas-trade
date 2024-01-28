from tefas import Crawler
from datetime import datetime, timedelta
import pandas as pd

# Create an instance of the Crawler
tefas = Crawler()

fund_name = 'YAY'

def get_previous_friday(date):
    while date.weekday() != 4:  # 4 corresponds to Friday
        date -= timedelta(days=1)
    return date

# ...

def get_profit_info(start_date, end_date, fund_name=fund_name):
    # Fetch the fund data
    data = tefas.fetch(start=start_date.strftime('%Y-%m-%d'), 
                       end=end_date.strftime('%Y-%m-%d'), 
                       name=fund_name, 
                       columns=['date', 'price'])
    
    # Convert the data to a DataFrame and sort it
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df.sort_values(by='date', inplace=True)

    # Convert 'price' column to float for calculations
    df['price'] = df['price'].astype(float)

    # Calculate the profit percentage
    start_price = df['price'].iloc[0]  # Price at the start of the period
    end_price = df['price'].iloc[-1]   # Price at the end of the period
    profit_percentage = ((end_price - start_price) / start_price) * 100
    
    # Return the start date, start price, and profit percentage
    return start_date.strftime('%Y-%m-%d'), start_price, profit_percentage


# Define the end date as today and adjust if it's a weekend
end_date = datetime.now()
if end_date.weekday() > 4:  # Saturday (5) or Sunday (6)
    end_date = get_previous_friday(end_date)

# Fetch the price for the most recent trading day (end_date)
today_data = tefas.fetch(start=end_date.strftime('%Y-%m-%d'), 
                         end=end_date.strftime('%Y-%m-%d'), 
                         name=fund_name, 
                         columns=['date', 'price'])
today_df = pd.DataFrame(today_data)
today_price = today_df['price'].iloc[-1] if not today_df.empty else None


# Calculate start dates for different periods
one_week_start = end_date - timedelta(weeks=1)
two_weeks_start = end_date - timedelta(weeks=2)
four_weeks_start = end_date - timedelta(weeks=4)
eight_weeks_start = end_date - timedelta(weeks=8)
twelve_weeks_start = end_date - timedelta(weeks=12)

# Adjust start dates to previous Friday if they fall on a weekend
one_week_start = get_previous_friday(one_week_start) if one_week_start.weekday() > 4 else one_week_start
two_weeks_start = get_previous_friday(two_weeks_start) if two_weeks_start.weekday() > 4 else two_weeks_start
four_weeks_start = get_previous_friday(four_weeks_start) if four_weeks_start.weekday() > 4 else four_weeks_start
eight_weeks_start = get_previous_friday(eight_weeks_start) if eight_weeks_start.weekday() > 4 else eight_weeks_start
twelve_weeks_start = get_previous_friday(twelve_weeks_start) if twelve_weeks_start.weekday() > 4 else twelve_weeks_start

# Get profit information for each period
info_one_week = get_profit_info(one_week_start, end_date)
info_two_weeks = get_profit_info(two_weeks_start, end_date)
info_four_weeks = get_profit_info(four_weeks_start, end_date)
info_eight_weeks = get_profit_info(eight_weeks_start, end_date)
info_twelve_weeks = get_profit_info(twelve_weeks_start, end_date)

# Print the results
print(f"{fund_name} Fund Profit Information:")
print(f"Today's Price (as of {end_date.strftime('%Y-%m-%d')}): {today_price}")
print(f"Last 1 week: {info_one_week[2]:.2f}%, Date: {info_one_week[0]}, Price: {info_one_week[1]}")
print(f"Last 2 weeks: {info_two_weeks[2]:.2f}%, Date: {info_two_weeks[0]}, Price: {info_two_weeks[1]}")
print(f"Last 4 weeks: {info_four_weeks[2]:.2f}%, Date: {info_four_weeks[0]}, Price: {info_four_weeks[1]}")
print(f"Last 8 weeks: {info_eight_weeks[2]:.2f}%, Date: {info_eight_weeks[0]}, Price: {info_eight_weeks[1]}")
print(f"Last 12 weeks: {info_twelve_weeks[2]:.2f}%, Date: {info_twelve_weeks[0]}, Price: {info_twelve_weeks[1]}")
