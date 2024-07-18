import yfinance as yf
import os
from datetime import datetime, timedelta
import logging
from config import TICKERS, DATA_DIRECTORY, INTERVALS
from logging_setup import setup_logging

setup_logging('download_data.log')

def get_start_date(interval):
    logging.debug(f"Calculating start date for interval {interval}")
    if INTERVALS[interval] is None:
        return None  # Use the full data available for '1d', '1wk', '1mo'
    return datetime.now() - timedelta(days=INTERVALS[interval])

def download_data(ticker, interval, directory):
    start_date = get_start_date(interval)
    end_date = datetime.now()
    logging.debug(f"Downloading data for {ticker} from {start_date} to {end_date} with interval {interval}")
    data = yf.download(ticker, start=start_date, end=end_date, interval=interval, progress=False)
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, f"{ticker}_{interval}.csv")
    data.to_csv(filename)
    logging.debug(f"Data for {ticker} ({interval}) saved to {filename}")
    return filename

def get_company_info(ticker):
    logging.debug(f"Fetching company info for {ticker}")
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "name": info.get("longName", "N/A"),
        "ticker": ticker,
        "country": info.get("country", "N/A"),
        "exchange": info.get("exchange", "N/A")
    }

if __name__ == "__main__":
    for ticker in TICKERS:
        for interval in INTERVALS:
            directory = os.path.join(DATA_DIRECTORY, interval)
            filename = os.path.join(directory, f"{ticker}_{interval}.csv")
            if not os.path.exists(filename):
                filename = download_data(ticker, interval, directory)
                logging.info(f"Data for {ticker} ({interval}) saved to {filename}")
            else:
                logging.info(f"Data for {ticker} ({interval}) already exists in {filename}")
