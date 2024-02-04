import pandas as pd
import os

# Directory of the script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Load the data
df_path = os.path.join(script_dir, 'all_fund_profit_percentages_api.csv')
df = pd.read_csv(df_path)

# Configurable periods
periods = [(1, 40), (2, 40), (4, 40), (6, 40), (8, 40), (10, 40), (12, 40), (14, 40), (16, 40), (18, 40), (20, 40), (22, 40), (24, 40)]

# Function to get top funds for a given period
def get_top_funds_for_period(df, weeks, top_n):
    latest_week = df.columns[-1].split()[0]
    relevant_weeks = [f"{int(latest_week) - i} Weeks" for i in range(weeks)]
    avg_weekly_performance = df[relevant_weeks].mean(axis=1)
    top_funds = avg_weekly_performance.nlargest(top_n).index
    return set(df.loc[top_funds, 'Fund'])

# Get the top funds for each period
top_funds_sets = [get_top_funds_for_period(df, weeks, top_n) for weeks, top_n in periods]

# Find the intersection of top funds across all specified periods
intersection_funds = set.intersection(*top_funds_sets)

# Filter the DataFrame to only include these top funds
df = df[df['Fund'].isin(intersection_funds)]

# Exclude funds based on keywords in 'Full Fund Name'
exclude_keywords = ['TEKNOLOJİ', 'TECHNOLOGY', 'BLOCKCHAIN', 'METAVERSE', 'TECHNOLOGIES', 'TEKNOLOGY']
excluded_funds = df[df['Full Fund Name'].apply(lambda x: any(keyword in str(x).upper() for keyword in exclude_keywords))]
included_funds = df[~df['Fund'].isin(excluded_funds['Fund'])]

# Creating a single DataFrame for both included and excluded funds
combined_df = pd.concat([
    pd.DataFrame({'Category': ['Non-filtered Funds'], 'Fund': [''], 'Full Fund Name': ['']}), 
    included_funds,
    pd.DataFrame({'Category': ['Filtered Funds'], 'Fund': [''], 'Full Fund Name': ['']}), 
    excluded_funds
], ignore_index=True)

# Writing the combined funds data to a CSV file in the script's directory
combined_output_path = os.path.join(script_dir, 'configurable_weeks_sort.csv')
combined_df.to_csv(combined_output_path, index=False)

print(f"Combined funds have been written to {combined_output_path}")
