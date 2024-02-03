from tefas import Crawler
import csv
from datetime import datetime

# Create an instance of the Crawler
tefas = Crawler()

# Read fund names from fund_names.txt
with open('fund_names.txt', 'r') as file:
    fund_names = file.read().splitlines()

# Define the dates for fetching the price information
start_date_price_date = "2023-12-22"  # Corrected date for fetching start date price
end_date_price_date = "2023-12-22"    # Date for fetching end date price

# Open a CSV file to write the fund data as it is processed
with open('fund_performance.csv', 'w', newline='') as csvfile:
    fieldnames = ['fund_name', 'fund_title', 'start_date', 'start_date_price', 'end_date', 'end_date_price', 'percentage_change']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Fetch and calculate the percentage change in price for each fund name
    for fund_name in fund_names:
        print(f"Processing {fund_name}...")
        try:
            # Fetch price information for the start date
            start_data = tefas.fetch(start=start_date_price_date, 
                                     end=start_date_price_date, 
                                     name=fund_name, 
                                     columns=['date', 'price', 'title'])
            start_price = start_data['price'].iloc[0] if not start_data.empty else None
            fund_title = start_data['title'].iloc[0] if not start_data.empty else None
        except Exception as e:
            print(f"Error fetching data for {fund_name} on start date: {e}")
            start_price, fund_title = None, None

        try:
            # Fetch price information for the end date
            end_data = tefas.fetch(start=end_date_price_date, 
                                   end=end_date_price_date, 
                                   name=fund_name, 
                                   columns=['date', 'price'])
            end_price = end_data['price'].iloc[0] if not end_data.empty else None
        except Exception as e:
            print(f"Error fetching data for {fund_name} on end date: {e}")
            end_price = None

        # Calculate the percentage change if both prices are available
        if start_price and end_price:
            percentage_change = ((end_price - start_price) / start_price) * 100
            fund_info = {
                'fund_name': fund_name,
                'fund_title': fund_title,
                'start_date': start_date_price_date,
                'start_date_price': start_price,
                'end_date': end_date_price_date,
                'end_date_price': end_price,
                'percentage_change': percentage_change
            }
            print(f"Data for {fund_name}: {fund_info}")
        else:
            fund_info = {
                'fund_name': fund_name,
                'fund_title': fund_title if fund_title else 'N/A',
                'start_date': start_date_price_date,
                'start_date_price': 'N/A',
                'end_date': end_date_price_date,
                'end_date_price': 'N/A',
                'percentage_change': 'N/A'
            }
            print(f"Data for {fund_name} is incomplete or not available.")

        # Write the fund information to the CSV file
        writer.writerow(fund_info)

# Read the data back from the CSV, sort it, and overwrite the file with sorted data
with open('fund_performance.csv', 'r', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    sorted_list = sorted(reader, key=lambda x: (x['percentage_change'] != 'N/A', float(x['percentage_change']) if x['percentage_change'] != 'N/A' else float('-inf')), reverse=True)

# Rewrite the sorted data to the CSV file
with open('fund_performance.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(sorted_list)

print("Processing complete. Data sorted and written to fund_performance.csv.")