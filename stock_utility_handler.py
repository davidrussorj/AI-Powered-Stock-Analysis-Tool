import pandas as pd
import json
from datetime import datetime
import pytz
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.widgets as widgets
import requests


class StockAPI:
    def __init__(self,api_key):
        self.api_key = api_key
        
    def get_stock_info(self,stock,market):
        if market == 'NASDAQ':
            url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock}&outputsize=compact&apikey={self.api_key}'
        else:
            url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock}.{market}&outputsize=compact&apikey={self.api_key}'
        r = requests.get(url)
        data = r.json()
        return data 
    
class StockAnalyzer:
    def __init__(self):
        pass

    def json_to_dataframe(self,json_data,stock_symbol,market):
        print(json_data)
        time_series_data = json_data['Time Series (Daily)']
        df_data = []

        for date_str, values in time_series_data.items():
            data_row = {'date': date_str}
            for key, value in values.items():
                new_key = key.split('. ')[1]  # Correctly extract the key
                data_row[new_key] = float(value)
            df_data.append(data_row)

        df = pd.DataFrame(df_data)
        df['date'] = pd.to_datetime(df['date'])

        eastern = pytz.timezone('US/Eastern')
        ist = pytz.timezone('Asia/Kolkata')

        df['date'] = df['date'].dt.tz_localize(eastern).dt.tz_convert(ist)
        df['date'] = df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        df['stock']=stock_symbol
        df['market']=market

        df = df.set_index('date')
        return df

    def plot_stock_data(self,df, stock_symbol, market,image_path):
        plt.figure(figsize=(16, 10))

        # Plotting Closing Price
        plt.subplot(3, 1, 1)
        plt.plot(pd.to_datetime(df.index), df['close'], label=f'{stock_symbol} Closing Price ({market})', color='blue')
        plt.title(f'{stock_symbol} Stock Performance ({market})')
        plt.xlabel('Date (IST)')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)

        # Plotting Volume
        plt.subplot(3, 1, 2)
        plt.bar(pd.to_datetime(df.index), df['volume'], label=f'{stock_symbol} Volume ({market})', color='green', width=2)
        plt.xlabel('Date (IST)')
        plt.ylabel('Volume')
        plt.legend()
        plt.grid(True)

        # Plotting Moving Averages
        plt.subplot(3, 1, 3)
        df['MA_7'] = df['close'].rolling(window=7).mean()
        df['MA_20'] = df['close'].rolling(window=20).mean()
        plt.plot(pd.to_datetime(df.index), df['close'], label=f'{stock_symbol} Closing Price ({market})', color='blue', alpha=0.7)
        plt.plot(pd.to_datetime(df.index), df['MA_7'], label='7-Day MA', color='orange')
        plt.plot(pd.to_datetime(df.index), df['MA_20'], label='20-Day MA', color='red')
        plt.xlabel('Date Month(IST)')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)

        # Enhanced Date Formatting for All Subplots
        for ax in plt.gcf().axes:
            # Major ticks every month, minor ticks every week
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=[0]))  # Monday

            # Formatter for major ticks
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

            # Formatter for minor ticks (hover tooltip will provide more detail)
            #ax.xaxis.set_minor_formatter(mdates.DateFormatter('%Y-%m-%d'))

            # Auto-rotate labels if needed
            plt.gcf().autofmt_xdate()

        # Add hover tooltip
        cursor = widgets.Cursor(plt.gca(), color='red', linewidth=1)

        plt.tight_layout()
        plt.savefig(image_path) 
        plt.show()