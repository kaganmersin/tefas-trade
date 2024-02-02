import pandas as pd
import os

# Ensure the output directory exists
output_folder = 'week_percentage_csv'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Load the data
df = pd.read_csv('all_fund_profit_percentages.csv')

# Configurable periods and top N funds for each period
periods = [(2, 50), (4, 50), (6, 50), (8, 50)]  # (weeks, top_n) pairs
# For example, (3, 50) means the top 50 funds over the last 3 weeks

# Function to get top funds for a given period
def get_top_funds_for_period(df, weeks, top_n):
    latest_week = df.columns[-1].split()[0]  # Assumes the last column is the latest week
    relevant_weeks = [f"{int(latest_week) - i} Weeks" for i in range(weeks)]
    avg_weekly_performance = df[relevant_weeks].mean(axis=1)
    top_funds = avg_weekly_performance.nlargest(top_n).index
    return set(df.loc[top_funds, 'Fund'])

# Get the top funds for each period
top_funds_sets = [get_top_funds_for_period(df, weeks, top_n) for weeks, top_n in periods]

# Find the intersection of top funds across all specified periods
intersection_funds = set.intersection(*top_funds_sets)

# Collecting the funds data
intersection_funds_data = df[df['Fund'].isin(intersection_funds)]

# Writing the intersection funds data to a CSV file
intersection_output_path = os.path.join(output_folder, 'intersection_funds_configurable_periods.csv')
intersection_funds_data.to_csv(intersection_output_path, index=False)

print(f"Intersection funds for configurable periods have been written to {intersection_output_path}")
