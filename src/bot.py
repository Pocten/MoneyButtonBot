import pandas as pd
from supertrend import strategy
from backtest import backtest, analyze_stocks
from plot_results import create_price_plots, load_stock_data
from config import TICKERS, START_DATE, END_DATE, DATA_DIRECTORY, TRADES_FILE
from download_data import download_data

def main():
    print("Starting bot...")

    results = analyze_stocks(TICKERS, START_DATE, END_DATE)

    trades_df = pd.read_csv(TRADES_FILE)
    stock_data = load_stock_data(TICKERS, DATA_DIRECTORY)
    create_price_plots(stock_data)

    for ticker, result in results.items():
        print(f"Ticker: {ticker}")
        print(f"Final Balance: ${result['Final Balance']:.2f}")
        print(f"Profit: ${result['Profit']:.2f}")
        print(f"Profit Percentage: {result['Profit Percentage']:.2f}%\n")

if __name__ == "__main__":
    main()
