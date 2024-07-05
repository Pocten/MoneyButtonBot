import pandas as pd
from supertrend import strategy
from backtest import backtest, analyze_stocks, plot_results
from config import TICKERS, START_DATE, END_DATE, DATA_DIRECTORY, INTERVAL
from download_data import download_data

def main():
    print("Starting bot...")

    results = analyze_stocks(TICKERS, START_DATE, END_DATE)

    plot_results(results)

    for ticker, result in results.items():
        print(f"Ticker: {ticker}")
        print(f"Final Balance: ${result['Final Balance']:.2f}")
        print(f"Profit: ${result['Profit']:.2f}")
        print(f"Profit Percentage: {result['Profit Percentage']:.2f}%\n")

if __name__ == "__main__":
    main()