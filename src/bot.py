import os
import pandas as pd
from tqdm import tqdm
import warnings
from supertrend import strategy
from backtest import backtest, analyze_stocks
from plot_results import create_price_plots, load_stock_data
from config import TICKERS, DATA_DIRECTORY, INTERVALS
from download_data import download_data
from results import generate_results_file
import itertools
import time
import threading
import sys
import traceback

# Функция анимации загрузки
def animate():
    print('\nBot is running...')
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if done:
            break
        tqdm.write(f'Loading {c}', end='\r')
        time.sleep(0.1)
    sys.stdout.write('\rBot is done!     \n')

done = False
t = threading.Thread(target=animate)
t.start()

def main():

    # Подавление предупреждений
    warnings.filterwarnings("ignore")

    # Скачивание данных с индикатором прогресса
    total_tasks = len(TICKERS) * len(INTERVALS)
    with tqdm(total=total_tasks, desc="Downloading data", ncols=100) as pbar:
        for ticker in TICKERS:
            for interval in INTERVALS:
                directory = os.path.join(DATA_DIRECTORY, interval)
                filename = os.path.join(directory, f"{ticker}_{interval}.csv")
                if not os.path.exists(filename):
                    download_data(ticker, interval, directory)
                pbar.update(1)

    # Анализ акций с индикатором прогресса
    results = analyze_stocks(TICKERS, DATA_DIRECTORY)

    # Создание графиков с индикатором прогресса
    for interval in tqdm(INTERVALS, desc="Creating price plots"):
        trades_file = os.path.join(DATA_DIRECTORY, interval, 'output', f"trades_{interval}.csv")
        if os.path.exists(trades_file):
            trades_df = pd.read_csv(trades_file)
            stock_data = load_stock_data(TICKERS, DATA_DIRECTORY, interval)
            create_price_plots(stock_data, trades_df, interval)
            generate_results_file(interval, trades_df)

    print("\nBot has successfully completed. Check the 'data' directory for results.\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("An error occurred:")
        traceback.print_exc()
    finally:
        done = True
        t.join()
