import pandas as pd
from strategy import strategy
from backtest import backtest, analyze_stocks, plot_results

def main():
    print("Starting bot...")
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "BABA", "V", "JNJ", "WMT"]
    start_date = "2019-05-26"
    end_date = "2024-05-26"

    # Скачиваем данные, если они еще не были скачаны
    download_data_for_tickers(tickers, start_date, end_date)

    # Выполняем анализ акций
    results = analyze_stocks(tickers, start_date, end_date)

    # Выводим результаты на графике
    plot_results(results)

    # Печатаем текстовую сводку результатов
    for ticker, result in results.items():
        print(f"Ticker: {ticker}")
        print(f"Final Balance: ${result['Final Balance']:.2f}")
        print(f"Profit: ${result['Profit']:.2f}")
        print(f"Profit Percentage: {result['Profit Percentage']:.2f}%\n")

def download_data_for_tickers(tickers, start_date, end_date):
    import yfinance as yf
    import os

    directory = "data/historical"
    if not os.path.exists(directory):
        os.makedirs(directory)

    for ticker in tickers:
        filename = os.path.join(directory, f"{ticker}.csv")
        if not os.path.isfile(filename):
            print(f"Downloading data for {ticker}...")
            data = yf.download(ticker, start=start_date, end=end_date)
            data.to_csv(filename)
            print(f"Data for {ticker} saved to {filename}")
        else:
            print(f"Data for {ticker} already exists.")

if __name__ == "__main__":
    main()
