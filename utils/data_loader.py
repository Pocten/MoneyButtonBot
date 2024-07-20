import os
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from config.config import TICKERS, INTERVALS
import logging

# Настройка логирования для yfinance на уровне ошибок
logging.getLogger('yfinance').setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

def get_start_date(interval):
    if INTERVALS[interval] is None:
        return None
    return datetime.now() - timedelta(days=INTERVALS[interval])

def download_data(ticker, interval):
    start_date = get_start_date(interval)
    end_date = datetime.now()
    logger.info(f"Downloading data for {ticker} from {start_date} to {end_date} with interval {interval}")
    try:
        data = yf.download(ticker, start=start_date, end=end_date, interval=interval, progress=False)
        if data.empty:
            raise ValueError(f"No data for {ticker} with interval {interval}")
    except Exception as e:
        logger.error(f"Failed to download data for {ticker} with interval {interval}: {e}")
        return None
    return data

def save_data(ticker, interval, data):
    directory = os.path.join('data', 'historical_data', interval)
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, f"{ticker}_{interval}.csv")
    data.to_csv(file_path)
    logger.info(f"Data for {ticker} saved to {file_path}")
    return file_path

def load_data(ticker, interval):
    file_path = os.path.join('data', 'historical_data', interval, f"{ticker}_{interval}.csv")
    if not os.path.exists(file_path):
        logger.info(f"Data file {file_path} not found, downloading data...")
        data = download_data(ticker, interval)
        if data is not None:
            save_data(ticker, interval, data)
    else:
        logger.info(f"Loading data from {file_path}")
        data = pd.read_csv(file_path, index_col=0, parse_dates=True)
    return data

def download_all_data():
    for ticker in TICKERS:
        for interval in INTERVALS:
            file_path = os.path.join('data', 'historical_data', interval, f"{ticker}_{interval}.csv")
            if not os.path.exists(file_path):
                data = download_data(ticker, interval)
                if data is not None:
                    save_data(ticker, interval, data)
            else:
                logger.info(f"Data for {ticker} ({interval}) already exists in {file_path}")

if __name__ == "__main__":
    download_all_data()
