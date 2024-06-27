import pandas as pd
import matplotlib.pyplot as plt
from strategy import strategy

def backtest(data, initial_balance=1000, take_profit_percent=0.15, stop_loss_percent=0.05):
    data = strategy(data)
    balance = initial_balance
    position = 0
    balance_over_time = []

    for index, row in data.iterrows():
        if row['BuySignal'] and position == 0:
            position = 1
            entry_price = row['close']
            take_profit_level = entry_price * (1 + take_profit_percent)
            stop_loss_level = entry_price * (1 - stop_loss_percent)
        elif row['SellSignal'] and position == 0:
            position = -1
            entry_price = row['close']
            take_profit_level = entry_price * (1 - take_profit_percent)
            stop_loss_level = entry_price * (1 + stop_loss_percent)
        elif position == 1:
            if row['close'] >= take_profit_level or row['close'] <= stop_loss_level:
                balance += (row['close'] - entry_price) * (balance / entry_price)
                position = 0
        elif position == -1:
            if row['close'] <= take_profit_level or row['close'] >= stop_loss_level:
                balance += (entry_price - row['close']) * (balance / entry_price)
                position = 0
        balance_over_time.append(balance)

    return balance, balance_over_time

def analyze_stocks(tickers, start_date, end_date):
    initial_balance = 1000
    results = {}

    for ticker in tickers:
        data = pd.read_csv(f'data/historical/{ticker}.csv')
        data = data.rename(columns=str.lower)  # Приведение всех имен столбцов к нижнему регистру
        if 'close' not in data.columns:
            raise KeyError(f"Data for {ticker} must contain 'close' column.")
        data['close'] = pd.to_numeric(data['close'], errors='coerce')
        data = data.dropna(subset=['close'])
        # Проверка длинны данных
        if len(data) < 55:
            print(f"Недостаточно данных для {ticker}. Пропущен.")
            continue
        print(f"Processing {ticker}, data length: {len(data)}")
        final_balance, balance_over_time = backtest(data, initial_balance)
        results[ticker] = {
            "Final Balance": final_balance,
            "Balance Over Time": balance_over_time,
            "Profit": final_balance - initial_balance,
            "Profit Percentage": (final_balance / initial_balance - 1) * 100
        }

    return results

def plot_results(results):
    fig, ax = plt.subplots()
    for ticker, result in results.items():
        ax.plot(result["Balance Over Time"], label=ticker)
    ax.set_xlabel('Time')
    ax.set_ylabel('Balance')
    ax.legend()
    plt.show()

if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "BABA", "V", "JNJ", "WMT"]
    start_date = "2019-05-26"
    end_date = "2024-05-26"

    results = analyze_stocks(tickers, start_date, end_date)
    plot_results(results)

    for ticker, result in results.items():
        print(f"Ticker: {ticker}")
        print(f"Final Balance: ${result['Final Balance']:.2f}")
        print(f"Profit: ${result['Profit']:.2f}")
        print(f"Profit Percentage: {result['Profit Percentage']:.2f}%\n")
