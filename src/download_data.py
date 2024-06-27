import yfinance as yf
import pandas as pd
import os

def download_data(ticker, start_date, end_date, directory):
    data = yf.download(ticker, start=start_date, end=end_date)
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, f"{ticker}.csv")
    data.to_csv(filename)
    return filename

if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "BABA", "V", "JNJ", "WMT"]
    start_date = "2019-05-26"
    end_date = "2024-05-26"
    directory = "data/historical"

    for ticker in tickers:
        filename = download_data(ticker, start_date, end_date, directory)
        print(f"Data for {ticker} saved to {filename}")
