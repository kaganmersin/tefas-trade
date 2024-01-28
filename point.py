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
today = datetime.now()
if today.weekday() > 4:  # Saturday (5) or Sunday (6)
    today = get_previous_friday(today)

# Fetch all funds information for today
all_funds_data = tefas.fetch(start=today.strftime('%Y-%m-%d'), columns=["code", "date", "price"])
all_funds_df = pd.DataFrame(all_funds_data)
all_funds = all_funds_df['code'].unique()

# Function to calculate fund points
def calculate_fund_points(fund_name):
    # Define the date periods
    end_date = datetime.now()
    if end_date.weekday() > 4:  # Saturday (5) or Sunday (6)
        end_date = get_previous_friday(end_date)
    
    one_week_start = end_date - timedelta(weeks=1)
    two_weeks_start = end_date - timedelta(weeks=2)
    four_weeks_start = end_date - timedelta(weeks=4)
    eight_weeks_start = end_date - timedelta(weeks=8)
    twelve_weeks_start = end_date - timedelta(weeks=12)

    # Get profit information for each period
    info_one_week = get_profit_info(one_week_start, end_date, fund_name)
    info_two_weeks = get_profit_info(two_weeks_start, end_date, fund_name)
    info_four_weeks = get_profit_info(four_weeks_start, end_date, fund_name)
    info_eight_weeks = get_profit_info(eight_weeks_start, end_date, fund_name)
    info_twelve_weeks = get_profit_info(twelve_weeks_start, end_date, fund_name)

    # Calculate points
    points = (info_one_week[2] * 32 +
              info_two_weeks[2] * 16 +
              info_four_weeks[2] * 8 +
              info_eight_weeks[2] * 4 +
              info_twelve_weeks[2] * 2)

    return points

with open('fund_points.txt', 'w') as file:
    for fund in all_funds:
        print(f"Processing {fund}...")  # Print before processing each fund
        points = calculate_fund_points(fund)
        file.write(f"{fund}: {points}\n")
        file.flush()  # Force flush the buffer to the file
        print(f"Processed {fund}: {points} - written to file")

print("Fund points have been written to fund_points.txt")

# Read the file contents
def safe_float_conversion(value):
    try:
        return float(value)
    except ValueError:  # Handles non-numeric values like 'nan' or 'inf'
        return float('-inf') if value == 'inf' else float('inf')

# Read the file contents
with open('fund_points.txt', 'r') as file:
    funds_with_points = [line.strip().split(': ') for line in file]

# Convert points to float safely and sort the list by points in descending order
funds_with_points.sort(key=lambda x: safe_float_conversion(x[1]), reverse=True)

# Write the sorted content back to the file
with open('fund_points_sorted.txt', 'w') as file:
    for fund, points in funds_with_points:
        file.write(f"{fund}: {points}\n")

print("Fund points have been sorted and written to fund_points_sorted.txt")