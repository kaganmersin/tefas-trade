from tefas import Crawler
from datetime import datetime, timedelta
import pandas as pd

# Create an instance of the Crawler
tefas = Crawler()

fund_name = 'YAY'


data = tefas.fetch(start="2023-06-15", 
                   end="2023-06-30", 
                   name=fund_name, 
                   columns=['date', 'price'])

print(data)  