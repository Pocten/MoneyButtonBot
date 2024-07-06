# backtest.py
import pandas as pd
from supertrend import strategy
from config import DATA_DIRECTORY, INITIAL_BALANCE, TAKE_PROFIT_PERCENT, STOP_LOSS_PERCENT, WHOLE_SHARES_ONLY, TICKERS, START_DATE, END_DATE

# Глобальный датафрейм для записи всех сделок
trades_df = pd.DataFrame(columns=['Ticker', 'Date', 'Trade Type', 'Action', 'Shares', 'Price', 'Profit', 'Balance'])

def record_trade(ticker, date, trade_type, action, shares, price, profit, balance):
    global trades_df
    trade_data = {
        'Ticker': ticker,
        'Date': pd.to_datetime(date).strftime('%d.%m.%Y %H:%M'),
        'Trade Type': trade_type,
        'Action': action,
        'Shares': shares,
        'Price': price,
        'Profit': profit,
        'Balance': balance
    }
    trades_df = pd.concat([trades_df, pd.DataFrame([trade_data])], ignore_index=True)

def backtest(data, ticker, initial_balance=INITIAL_BALANCE, take_profit_percent=TAKE_PROFIT_PERCENT, stop_loss_percent=STOP_LOSS_PERCENT, whole_shares_only=WHOLE_SHARES_ONLY):
    data = strategy(data)
    balance = initial_balance
    position = 0
    shares = 0
    balance_over_time = []
    last_potential_trade = None

    for index, row in data.iterrows():
        if row['in_flat']:
            if row['BuySignal']:
                last_potential_trade = ('buy', row['close'])
            elif row['SellSignal']:
                last_potential_trade = ('sell', row['close'])
            balance_over_time.append(balance)
            continue

        if last_potential_trade and not row['in_flat']:
            trade_type, entry_price = last_potential_trade
            last_potential_trade = None
            if trade_type == 'buy' and position == 0:
                position = 1
                take_profit_level = entry_price * (1 + take_profit_percent)
                stop_loss_level = entry_price * (1 - stop_loss_percent)
                shares = balance // entry_price if whole_shares_only else balance / entry_price
                balance -= shares * entry_price
                record_trade(ticker, row.name, 'Long', 'Open', shares, entry_price, 0, balance)
            elif trade_type == 'sell' and position == 0:
                position = -1
                take_profit_level = entry_price * (1 - take_profit_percent)
                stop_loss_level = entry_price * (1 + stop_loss_percent)
                shares = balance // entry_price if whole_shares_only else balance / entry_price
                balance += shares * entry_price  # Correction here to add the short sell amount to balance
                record_trade(ticker, row.name, 'Short', 'Open', shares, entry_price, 0, balance)
            continue

        if row['BuySignal'] and position == 0:
            position = 1
            entry_price = row['close']
            take_profit_level = entry_price * (1 + take_profit_percent)
            stop_loss_level = entry_price * (1 - take_profit_percent)
            shares = balance // entry_price if whole_shares_only else balance / entry_price
            balance -= shares * entry_price
            record_trade(ticker, row.name, 'Long', 'Open', shares, entry_price, 0, balance)
        elif row['SellSignal'] and position == 1:
            profit = (row['close'] - entry_price) * shares
            balance += shares * row['close']
            record_trade(ticker, row.name, 'Long', 'Close', shares, row['close'], profit, balance)
            position = 0
        elif row['SellSignal'] and position == 0:
            position = -1
            entry_price = row['close']
            take_profit_level = entry_price * (1 - take_profit_percent)
            stop_loss_level = entry_price * (1 + stop_loss_percent)
            shares = balance // entry_price if whole_shares_only else balance / entry_price
            balance += shares * entry_price  # Correction here to add the short sell amount to balance
            record_trade(ticker, row.name, 'Short', 'Open', shares, entry_price, 0, balance)
        elif row['BuySignal'] and position == -1:
            profit = (entry_price - row['close']) * shares
            balance -= shares * row['close']  # Correction here to subtract the amount needed to cover the short
            record_trade(ticker, row.name, 'Short', 'Close', shares, row['close'], profit, balance)
            position = 0
        elif position == 1:
            if row['close'] >= take_profit_level or row['close'] <= stop_loss_level:
                profit = (row['close'] - entry_price) * shares
                balance += shares * row['close']
                record_trade(ticker, row.name, 'Long', 'Close', shares, row['close'], profit, balance)
                position = 0
        elif position == -1:
            if row['close'] <= take_profit_level or row['close'] >= stop_loss_level:
                profit = (entry_price - row['close']) * shares
                balance -= shares * row['close']  # Correction here to subtract the amount needed to cover the short
                record_trade(ticker, row.name, 'Short', 'Close', shares, row['close'], profit, balance)
                position = 0
        balance_over_time.append(balance)

    # Close any open positions at the end of the period
    if position != 0:
        if position == 1:
            profit = (data.iloc[-1]['close'] - entry_price) * shares
            balance += shares * data.iloc[-1]['close']
            record_trade(ticker, data.index[-1], 'Long', 'Close', shares, data.iloc[-1]['close'], profit, balance)
        elif position == -1:
            profit = (entry_price - data.iloc[-1]['close']) * shares
            balance -= shares * data.iloc[-1]['close']  # Correction here to subtract the amount needed to cover the short
            record_trade(ticker, data.index[-1], 'Short', 'Close', shares, data.iloc[-1]['close'], profit, balance)

    return balance, balance_over_time

def analyze_stocks(tickers, start_date, end_date):
    global trades_df
    trades_df = pd.DataFrame(columns=['Ticker', 'Date', 'Trade Type', 'Action', 'Shares', 'Price', 'Profit', 'Balance'])

    initial_balance = INITIAL_BALANCE
    results = {}

    for ticker in tickers:
        data = pd.read_csv(f'{DATA_DIRECTORY}/{ticker}_hourly.csv', index_col=0, parse_dates=True)
        data = data.rename(columns=str.lower)
        if 'close' not in data.columns:
            raise KeyError(f"Data for {ticker} must contain 'close' column.")
        data['close'] = pd.to_numeric(data['close'], errors='coerce')
        data = data.dropna(subset=['close'])
        if len(data) < 55:
            print(f"Недостаточно данных для {ticker}. Пропущен.")
            continue
        print(f"Processing {ticker}, data length: {len(data)}")
        final_balance, balance_over_time = backtest(data, ticker, initial_balance)
        results[ticker] = {
            "Final Balance": final_balance,
            "Balance Over Time": balance_over_time,
            "Profit": final_balance - initial_balance,
            "Profit Percentage": (final_balance / initial_balance - 1) * 100
        }

    # Save trades to a CSV file
    trades_df.to_csv("trades.csv", index=False)
    return results
