import yfinance as yf
import os
from datetime import datetime, timedelta
from config import TICKERS, START_DATE, END_DATE, DATA_DIRECTORY, INTERVAL

def download_data(ticker, start_date, end_date, directory, interval='1h'):
    data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, f"{ticker}_hourly.csv")
    data.to_csv(filename)
    return filename

if __name__ == "__main__":
    for ticker in TICKERS:
        filename = download_data(ticker, START_DATE, END_DATE, DATA_DIRECTORY, interval=INTERVAL)
        print(f"Data for {ticker} saved to {filename}")