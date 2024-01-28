import pandas as pd
import os

# Ensure the week_percentage_csv directory exists
output_folder = 'week_percentage_csv'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Load the data
df = pd.read_csv('all_fund_profit_percentages.csv')

# Define the number of top funds for each period
top_n_first_period = 140
top_n_second_period = 80
first_period_weeks = 8  # Weeks 1 to 6
second_period_weeks = 18  # Weeks 7 to 14

# Get the top funds for weeks 1 to 6 (top 100) and weeks 7 to 14 (top 50)
top_funds = [set(df.nlargest(top_n_first_period if i <= first_period_weeks else top_n_second_period, f'{i} Weeks')['Fund']) for i in range(1, second_period_weeks + 1)]

# Find the intersection of top funds from any two of the weeks 1 to 6 with all weeks from 7 to 14
intersection_of_top_funds_first_period = set.union(*[set.intersection(top_funds[i], top_funds[j]) for i in range(first_period_weeks) for j in range(i+1, first_period_weeks)])
intersection_funds = set.intersection(intersection_of_top_funds_first_period, *top_funds[first_period_weeks:])

# Define the minimum percentage threshold and the number of recent weeks to check
min_percentage_threshold = 0.0  # Can be a negative number or a float like 1.5
lookback_weeks = 3  # Number of recent weeks to evaluate

# Calculate the average percentage and sort the funds
intersection_funds_data = []

for fund in intersection_funds:
    fund_data = df[df['Fund'] == fund].iloc[0]
    percentages = fund_data[[f'{i} Weeks' for i in range(1, second_period_weeks + 1)]].tolist()
    # Check if the fund has percentages above the threshold in the last lookback_weeks
    if all(x >= min_percentage_threshold for x in percentages[-lookback_weeks:]):
        average_percentage = sum(percentages) / len(percentages)
        # Format the average percentage to three decimal places with trailing zeros if necessary
        average_percentage = f"{average_percentage:.3f}"
        intersection_funds_data.append((fund, fund_data['Full Fund Name'], average_percentage, percentages))

# Sort the list by average percentage in descending order
intersection_funds_data.sort(key=lambda x: x[2], reverse=True)

# Write the sorted intersection funds to a CSV file
with open(os.path.join(output_folder, 'intersection_funds.csv'), 'w') as file:
    file.write('Fund,Full Fund Name,Average Percentage,' + ','.join([f'{i} Weeks' for i in range(1, second_period_weeks + 1)]) + '\n')
    for fund_info in intersection_funds_data:
        fund, full_fund_name, average_percentage, percentages = fund_info
        # Format the percentages to three decimal places with trailing zeros if necessary
        percentages_str = ','.join(f"{p:.3f}" for p in percentages)
        file.write(f"{fund},{full_fund_name},{average_percentage},{percentages_str}\n")

# Write the top funds for each week to separate CSV files with their full names
for i in range(1, second_period_weeks + 1):
    top_n = top_n_first_period if i <= first_period_weeks else top_n_second_period
    top_funds_with_percentage = df.nlargest(top_n, f'{i} Weeks')[['Fund', 'Full Fund Name', f'{i} Weeks']]
    # Format the percentages to three decimal places
    top_funds_with_percentage[f'{i} Weeks'] = top_funds_with_percentage[f'{i} Weeks'].apply(lambda x: f"{x:.3f}")
    output_path = os.path.join(output_folder, f'top_{top_n}_week_{i}.csv')
    top_funds_with_percentage.to_csv(output_path, index=False)

print(f"Intersection funds sorted by average percentage have been written to {os.path.join(output_folder, 'intersection_funds.csv')}")
print(f"Top funds for weeks 1 to {second_period_weeks} with full names have been written to the {output_folder} folder.")


# Keywords to exclude from the fund titles
exclude_keywords = ['TEKNOLOJİ', 'TECHNOLOGY', 'BLOCKCHAIN', 'METAVERSE', 'TECHNOLOGIES', 'TEKNOLOGY']

# Read the intersection funds CSV file
intersection_funds_df = pd.read_csv(os.path.join(output_folder, 'intersection_funds.csv'))

# Filter out funds that contain any of the exclude keywords in their 'Full Fund Name'
filtered_funds_df = intersection_funds_df[~intersection_funds_df['Full Fund Name'].str.contains('|'.join(exclude_keywords), case=False)]

# Write the filtered funds to a new CSV file
filtered_output_path = os.path.join(output_folder, 'filtered_intersection_funds.csv')
filtered_funds_df.to_csv(filtered_output_path, index=False)

# Update the original intersection funds CSV file by removing the filtered out funds
intersection_funds_df.drop(filtered_funds_df.index, inplace=True)
intersection_funds_df.to_csv(os.path.join(output_folder, 'intersection_funds.csv'), index=False)

print(f"Filtered funds have been written to {filtered_output_path}")
print(f"Updated intersection funds have been written to {os.path.join(output_folder, 'intersection_funds.csv')}")
