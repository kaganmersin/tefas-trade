import pandas as pd
import os

# Directory of the script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Configurable periods for each file
file_periods = {
    "all_fund_percentages-0-72.csv":  [(1, 30), (2, 30), (4, 30), (6, 30), (8, 25), (10, 24), (12, 23), (14, 22), (16, 10), (18, 10), (20, 10), (22, 10)],
    "all_fund_percentages-13-72.csv": [(1, 30), (2, 30), (4, 30), (6, 30), (8, 25), (10, 24), (12, 23), (14, 22), (16, 10), (18, 10), (20, 10), (22, 10)],
    "all_fund_percentages-25-72.csv": [(1, 30), (2, 30), (4, 30), (6, 30), (8, 25), (10, 24), (12, 23), (14, 22), (16, 10), (18, 10), (20, 10), (22, 10)],
    "all_fund_percentages-37-72.csv": [(1, 30), (2, 30), (4, 30), (6, 30), (8, 25), (10, 24), (12, 23), (14, 22), (16, 10), (18, 10), (20, 10), (22, 10)],
    "all_fund_percentages-49-72.csv": [(1, 30), (2, 30), (4, 30), (6, 30), (8, 25), (10, 24), (12, 23), (14, 22), (16, 10), (18, 10), (20, 10), (22, 10)],
}

# Function to get top funds for a given period
def get_top_funds_for_period(df, weeks, top_n):
    latest_week = df.columns[-1].split()[0]
    relevant_weeks = [f"{int(latest_week) - i} Weeks" for i in range(weeks)]
    avg_weekly_performance = df[relevant_weeks].mean(axis=1)
    top_funds = avg_weekly_performance.nlargest(top_n).index
    return set(df.loc[top_funds, 'Fund'])

# Process each file with its specific periods
for file, periods in file_periods.items():
    df_path = os.path.join(script_dir, file)
    df = pd.read_csv(df_path)

    # Get the top funds for each period specific to the file
    top_funds_sets = [get_top_funds_for_period(df, weeks, top_n) for weeks, top_n in periods]

    # Find the intersection of top funds across all specified periods
    intersection_funds = set.intersection(*top_funds_sets)

    # Filter the DataFrame to only include these top funds
    df = df[df['Fund'].isin(intersection_funds)]

    # Exclude funds based on keywords in 'Full Fund Name'
    exclude_keywords = ['TEKNOLOJİ', 'TECHNOLOGY', 'BLOCKCHAIN', 'METAVERSE', 'TECHNOLOGIES', 'TEKNOLOGY']
    excluded_funds = df[df['Full Fund Name'].apply(lambda x: any(keyword in str(x).upper() for keyword in exclude_keywords))]
    included_funds = df[~df['Fund'].isin(excluded_funds['Fund'])]

    # Exclude percentage columns from included_funds and excluded_funds
    columns_to_keep = ['Fund', 'Full Fund Name']
    included_funds = included_funds[columns_to_keep]
    excluded_funds = excluded_funds[columns_to_keep]

    # Creating a single DataFrame for both included and excluded funds
    combined_df = pd.concat([
        pd.DataFrame({'Category': ['Non-filtered Funds'], 'Fund': [''], 'Full Fund Name': ['']}), 
        included_funds,
        pd.DataFrame({'Category': ['Filtered Funds'], 'Fund': [''], 'Full Fund Name': ['']}), 
        excluded_funds
    ], ignore_index=True)

    # Output file name and saving the DataFrame
    output_file = file.replace('percentages', 'sorted')
    combined_output_path = os.path.join(script_dir, output_file)
    combined_df.to_csv(combined_output_path, index=False)

    print(f"Combined funds have been written to {combined_output_path}")
