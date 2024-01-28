from tefas import Crawler
from datetime import datetime, timedelta
import pandas as pd

df = pd.read_csv('all_fund_profit_percentages.csv')

sort_count = 50

# Get the top funds for each time period
def get_top_funds(df, period, top_n):
    return set(df.nlargest(top_n, period)['Fund'])

# Define variables for the number of top funds and week ranges
top_n_first_period = 100
top_n_second_period = 50
first_period_weeks = 6  # Weeks 1 to 6
second_period_weeks = 12  # Weeks 7 to 12

# Get the top funds for weeks 1 to 6 (top 100) and weeks 7 to 12 (top 50)
top_funds = [get_top_funds(df, f'{i} Weeks', top_n_first_period if i <= first_period_weeks else top_n_second_period) for i in range(1, second_period_weeks + 1)]

# Create a dictionary to hold the fund percentages for each week
fund_percentages = {week: df.nlargest(top_n_first_period if week <= first_period_weeks else top_n_second_period, f'{week} Weeks').set_index('Fund')[f'{week} Weeks'] for week in range(1, second_period_weeks + 1)}

# Find the intersection of top funds from any two of the weeks 1 to 6 with all weeks from 7 to 12
any_two_of_first_six_weeks = set.union(*[set.intersection(top_funds[i], top_funds[j]) for i in range(first_period_weeks) for j in range(i+1, first_period_weeks)])
intersection_funds = set.intersection(any_two_of_first_six_weeks, *top_funds[first_period_weeks:])

# Write the intersection funds and their percentages for weeks 1 to 12 to a file
with open('intersection_funds.txt', 'w') as file:
    for fund in intersection_funds:
        percentages = [fund_percentages[week].get(fund, 'N/A') for week in range(1, second_period_weeks + 1)]
        percentages_str = ','.join(map(str, percentages))
        file.write(f"{fund},{percentages_str}\n")

print(f"Intersection funds and their percentages for weeks 1 to {second_period_weeks} have been written to intersection_funds.txt")

# Get the top funds for each time period in descending order along with their percentages
def get_top_funds_with_percentage(df, period, top_n):
    sorted_funds = df.nlargest(top_n, period)[['Fund', period]]
    return sorted_funds

# Get top funds for weeks 1 to 12 and write to separate files with their percentages in descending order
for i in range(1, 13):
    top_funds_with_percentage = get_top_funds_with_percentage(df, f'{i} Weeks', sort_count)
    with open(f'top_100_week_{i}.csv', 'w') as file:
        for index, row in top_funds_with_percentage.iterrows():
            file.write(f"{row['Fund']},{row[f'{i} Weeks']}\n")

    print(f"Top 100 funds for week {i} with percentages have been written to top_100_week_{i}.csv in descending order")