import aiohttp
import asyncio
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import os
from tqdm.asyncio import tqdm_asyncio

# Function to get the previous Friday's date
def get_previous_friday(date):
    while date.weekday() != 4:
        date -= timedelta(days=1)
    return date

# Async function to fetch fund data with retry and concurrency control
async def fetch_fund_data(session, fund_code, start_date, end_date, semaphore, retries=3):
    url = 'https://www.tefas.gov.tr/api/DB/BindHistoryInfo'
    payload = {
        'fontip': 'YAT',
        'sfontur': '',
        'fonkod': fund_code,
        'fongrup': '',
        'bastarih': start_date.strftime('%d.%m.%Y'),
        'bittarih': end_date.strftime('%d.%m.%Y'),
        'fonturkod': '',
        'fonunvantip': ''
    }
    for attempt in range(retries):
        try:
            async with semaphore:
                async with session.post(url, data=payload, timeout=20) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return pd.DataFrame(data['data'])
        except Exception:
            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                return pd.DataFrame()

# Async function to get single day price
async def get_single_day_price(session, date, fund_code, semaphore):
    df = await fetch_fund_data(session, fund_code, date, date, semaphore)
    if not df.empty:
        price = df['FIYAT'].astype(float).iloc[0]
        price = f"{price:.3f}"
        full_fund_name = df['FONUNVAN'].iloc[0]
        return price, full_fund_name
    else:
        return None, None

# Async function to get the most recent price
async def get_recent_price_from_date(session, fund_code, base_date, semaphore):
    for days_back in range(3):
        date_to_check = base_date - timedelta(days=days_back)
        price, _ = await get_single_day_price(session, date_to_check, fund_code, semaphore)
        if price is not None:
            return price
    return None

async def process_fund(session, fund, today, week_dates, number_of_weeks, semaphore):
    try:
        weekly_profits = []
        weekly_prices = []
        full_fund_name = ''
        today_price = await get_recent_price_from_date(session, fund, today, semaphore)

        for week, date in enumerate(week_dates, 1):
            start_price, name = await get_single_day_price(session, date, fund, semaphore)
            if week == 1 and name:
                full_fund_name = name

            if start_price is None:
                start_price = await get_recent_price_from_date(session, fund, date, semaphore)

            if start_price is not None:
                weekly_prices.append(start_price)
                if today_price is not None and float(start_price) != 0:
                    profit_percentage = ((float(today_price) - float(start_price)) / float(start_price)) * 100
                    profit_percentage = f"{profit_percentage:.3f}"
                    weekly_profits.append(profit_percentage)
                else:
                    weekly_profits.append('None')
            else:
                weekly_profits.append('None')
                weekly_prices.append('None')

        return fund, full_fund_name, today_price, weekly_profits, weekly_prices

    except Exception:
        return fund, '', 'None', ['None']*number_of_weeks, ['None']*number_of_weeks

async def main():
    today = datetime.now() - timedelta(days=1)
    if today.weekday() > 4:
        today = get_previous_friday(today)

    script_dir = Path(__file__).parent
    fund_names_path = script_dir / 'fund_names.txt'

    try:
        with open(fund_names_path, 'r', encoding='utf-8') as file:
            all_funds = [line.strip() for line in file]
    except FileNotFoundError:
        print(f"Error: The file 'fund_names.txt' was not found in {script_dir}.")
        return

    number_of_weeks = 74
    week_dates = [today - timedelta(weeks=week) for week in range(1, number_of_weeks + 1)]
    week_dates_str = [date.strftime('%Y-%m-%d') for date in week_dates]

    profit_csv_path = script_dir / 'all_fund_profit_percentages_api.csv'
    price_csv_path = script_dir / 'all_fund_prices_api.csv'

    today_str = today.strftime('%Y-%m-%d')

    semaphore = asyncio.Semaphore(5)

    async with aiohttp.ClientSession() as session:
        tasks = [process_fund(session, fund, today, week_dates, number_of_weeks, semaphore) for fund in all_funds]
        results = await tqdm_asyncio.gather(*tasks)

    # Write to files
    with open(profit_csv_path, 'w', encoding='utf-8') as profit_file, open(price_csv_path, 'w', encoding='utf-8') as price_file:
        price_header = 'Fund,Full Fund Name,Start Date (' + today_str + '),' + ','.join([f'{i} Weeks ({date})' for i, date in enumerate(week_dates_str, start=1)]) + '\n'
        price_file.write(price_header)

        profit_header = 'Fund,Full Fund Name,' + ','.join([f'{i} Weeks' for i in range(1, number_of_weeks + 1)]) + '\n'
        profit_file.write(profit_header)

        for fund, full_fund_name, today_price, weekly_profits, weekly_prices in results:
            profit_file.write(f"{fund},{full_fund_name},{','.join(weekly_profits)}\n")
            price_file.write(f"{fund},{full_fund_name},{today_price if today_price else 'None'},{','.join(weekly_prices)}\n")

    print("All profit percentages and prices have been written to their respective CSV files.")

if __name__ == '__main__':
    asyncio.run(main())
