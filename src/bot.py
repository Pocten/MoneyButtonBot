import os
import pandas as pd
from tqdm import tqdm
import warnings
import itertools
import time
import threading
import sys
import traceback
import logging
from strategies import strategies
from backtest import backtest, analyze_stocks
from plot_results import create_price_plots, load_stock_data
from config import TICKERS, DATA_DIRECTORY, INTERVALS
from download_data import download_data
from results import generate_results_file
from logging_setup import setup_logging

setup_logging('bot.log')

def animate():
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if done:
            break
        sys.stdout.write(f'\rLoading {c}')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\rBot is finished!     \n')

done = False
t = threading.Thread(target=animate)
t.start()

def main():
    logging.debug("Starting bot execution")
    warnings.filterwarnings("ignore")

    total_tasks = len(TICKERS) * len(INTERVALS)
    with tqdm(total=total_tasks, desc="Downloading data", ncols=100) as pbar:
        for ticker in TICKERS:
            for interval in INTERVALS:
                directory = os.path.join(DATA_DIRECTORY, interval)
                filename = os.path.join(directory, f"{ticker}_{interval}.csv")
                if not os.path.exists(filename):
                    logging.debug(f"Downloading data for {ticker} ({interval})")
                    download_data(ticker, interval, directory)
                pbar.update(1)

    results = {}
    for strategy_name, strategy_func in strategies.items():
        logging.debug(f"Analyzing stocks with strategy {strategy_name}")
        strategy_results = analyze_stocks(TICKERS, DATA_DIRECTORY, strategy_name, strategy_func)
        results[strategy_name] = strategy_results

    for strategy_name in strategies.keys():
        for interval in tqdm(INTERVALS, desc=f"Creating price plots for {strategy_name}"):
            trades_file = os.path.join(DATA_DIRECTORY, 'strategy_results', strategy_name, interval, 'output', f"trades_{interval}.csv")
            if os.path.exists(trades_file):
                trades_df = pd.read_csv(trades_file)
                if not trades_df.empty:
                    logging.debug(f"Creating price plots for {strategy_name} ({interval})")
                    stock_data = load_stock_data(TICKERS, DATA_DIRECTORY, interval)
                    create_price_plots(stock_data, trades_df, interval, strategy_name)
                    generate_results_file(interval, trades_df, strategy_name)
                else:
                    logging.debug(f"No trades found for strategy {strategy_name} in interval {interval}")

    logging.debug("Bot has successfully completed")
    print("\nBot has successfully completed. Check the 'data' directory for results.\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error("An error occurred", exc_info=True)
        print("An error occurred:")
        traceback.print_exc()
    finally:
        done = True
        t.join()
