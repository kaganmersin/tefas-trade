import requests
import pandas as pd
from datetime import datetime, timedelta
import os

def fetch_fund_returns(start_date, end_date):
    url = 'https://www.tefas.gov.tr/api/DB/BindComparisonFundReturns'
    payload = {
        'calismatipi': '1',
        'fontip': 'YAT',
        'sfontur': '',
        'kurucukod': '',
        'fongrup': '',
        'bastarih': start_date.strftime('%d.%m.%Y'),
        'bittarih': end_date.strftime('%d.%m.%Y'),
        'fonturkod': '',
        'fonunvantip': '',
        'strperiod': '1,1,1,1,1,1,1',
        'islemdurum': '1'
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data['data'])
    except requests.RequestException as e:
        print(f"API request failed: {e}")
        return pd.DataFrame()

def main():
    today = datetime.now()

    # Directory of the script
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Path for the CSV file
    csv_file_path = os.path.join(script_dir, 'fund_return_percentages_with_api.csv')

    fund_returns = {}

    for week in range(1, 56):
        start_date = today - timedelta(days=week * 7)
        df = fetch_fund_returns(start_date, today)

        for index, row in df.iterrows():
            fund_code = row['FONKODU']
            if fund_code not in fund_returns:
                fund_returns[fund_code] = {'name': row['FONUNVAN'], 'returns': [''] * 55}
            fund_returns[fund_code]['returns'][week - 1] = str(row['GETIRIORANI'])

    with open(csv_file_path, 'w') as file:
        file.write('Fund Code,Fund Name,' + ','.join([f'{i} Week Return' for i in range(1, 56)]) + '\n')
        for fund_code, data in fund_returns.items():
            file.write(f"{fund_code},{data['name']},{','.join(data['returns'])}\n")

    print("Fund return percentages have been written to the CSV file.")

if __name__ == "__main__":
    main()
