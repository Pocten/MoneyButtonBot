import pandas as pd
import os
import logging
from config import DATA_DIRECTORY, INTERVALS, INITIAL_BALANCE, TAKE_PROFIT_PERCENT, STOP_LOSS_PERCENT, WHOLE_SHARES_ONLY, TICKERS
from logging_setup import setup_logging

setup_logging('backtest.log')

def record_trade(trades_df, ticker, date, trade_type, action, shares, price, profit, balance):
    logging.debug(f"Recording trade: {ticker} {trade_type} {action} {shares} shares at {price}")
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
    return pd.concat([trades_df, pd.DataFrame([trade_data])], ignore_index=True)

def backtest(data, ticker, interval, strategy, strategy_params, initial_balance=INITIAL_BALANCE, take_profit_percent=TAKE_PROFIT_PERCENT, stop_loss_percent=STOP_LOSS_PERCENT, whole_shares_only=WHOLE_SHARES_ONLY):
    logging.debug(f"Starting backtest for {ticker} on interval {interval} with strategy {strategy.__name__}")

    balance = initial_balance
    position = 0
    shares = 0
    balance_over_time = []
    trades_df = pd.DataFrame(columns=['Ticker', 'Date', 'Trade Type', 'Action', 'Shares', 'Price', 'Profit', 'Balance'])
    last_potential_trade = None

    logging.debug(f"Initial balance: {balance}")

    for index, row in data.iterrows():
        if 'in_flat' in row and row['in_flat']:
            logging.debug(f"{row.name}: In flat market condition")
            if 'BuySignal' in row and row['BuySignal']:
                last_potential_trade = ('buy', row['close'])
                logging.debug(f"Buy signal detected, potential trade recorded at price {row['close']}")
            elif 'SellSignal' in row and row['SellSignal']:
                last_potential_trade = ('sell', row['close'])
                logging.debug(f"Sell signal detected, potential trade recorded at price {row['close']}")
            balance_over_time.append(balance)
            continue

        if last_potential_trade and 'in_flat' in row and not row['in_flat']:
            trade_type, entry_price = last_potential_trade
            last_potential_trade = None
            logging.debug(f"{row.name}: Exiting flat market condition, executing potential {trade_type} trade at price {entry_price}")
            if trade_type == 'buy' and position == 0:
                position = 1
                take_profit_level = entry_price * (1 + take_profit_percent)
                stop_loss_level = entry_price * (1 - stop_loss_percent)
                shares = balance // entry_price if whole_shares_only else balance / entry_price
                balance -= shares * entry_price
                trades_df = record_trade(trades_df, ticker, row.name, 'Long', 'Open', shares, entry_price, 0, balance)
            elif trade_type == 'sell' and position == 0:
                position = -1
                take_profit_level = entry_price * (1 - take_profit_percent)
                stop_loss_level = entry_price * (1 + stop_loss_percent)
                shares = balance // entry_price if whole_shares_only else balance / entry_price
                balance += shares * entry_price
                trades_df = record_trade(trades_df, ticker, row.name, 'Short', 'Open', shares, entry_price, 0, balance)
            continue

        if 'BuySignal' in row and row['BuySignal'] and position == 0:
            position = 1
            entry_price = row['close']
            take_profit_level = entry_price * (1 + take_profit_percent)
            stop_loss_level = entry_price * (1 - stop_loss_percent)
            shares = balance // entry_price if whole_shares_only else balance / entry_price
            balance -= shares * entry_price
            trades_df = record_trade(trades_df, ticker, row.name, 'Long', 'Open', shares, entry_price, 0, balance)
            logging.debug(f"{row.name}: Long position opened at price {entry_price}")
        elif 'SellSignal' in row and row['SellSignal'] and position == 1:
            profit = (row['close'] - entry_price) * shares
            balance += shares * row['close']
            trades_df = record_trade(trades_df, ticker, row.name, 'Long', 'Close', shares, row['close'], profit, balance)
            position = 0
            logging.debug(f"{row.name}: Long position closed at price {row['close']} with profit {profit}")
        elif 'SellSignal' in row and row['SellSignal'] and position == 0:
            position = -1
            entry_price = row['close']
            take_profit_level = entry_price * (1 - take_profit_percent)
            stop_loss_level = entry_price * (1 + stop_loss_percent)
            shares = balance // entry_price if whole_shares_only else balance / entry_price
            balance += shares * entry_price
            trades_df = record_trade(trades_df, ticker, row.name, 'Short', 'Open', shares, entry_price, 0, balance)
            logging.debug(f"{row.name}: Short position opened at price {entry_price}")
        elif 'BuySignal' in row and row['BuySignal'] and position == -1:
            profit = (entry_price - row['close']) * shares
            balance -= shares * row['close']
            trades_df = record_trade(trades_df, ticker, row.name, 'Short', 'Close', shares, row['close'], profit, balance)
            position = 0
            logging.debug(f"{row.name}: Short position closed at price {row['close']} with profit {profit}")
        elif position == 1:
            if row['close'] >= take_profit_level or row['close'] <= stop_loss_level:
                profit = (row['close'] - entry_price) * shares
                balance += shares * row['close']
                trades_df = record_trade(trades_df, ticker, row.name, 'Long', 'Close', shares, row['close'], profit, balance)
                position = 0
                logging.debug(f"{row.name}: Long position closed at price {row['close']} due to {'take profit' if row['close'] >= take_profit_level else 'stop loss'} with profit {profit}")
        elif position == -1:
            if row['close'] <= take_profit_level or row['close'] >= stop_loss_level:
                profit = (entry_price - row['close']) * shares
                balance -= shares * row['close']
                trades_df = record_trade(trades_df, ticker, row.name, 'Short', 'Close', shares, row['close'], profit, balance)
                position = 0
                logging.debug(f"{row.name}: Short position closed at price {row['close']} due to {'take profit' if row['close'] <= take_profit_level else 'stop loss'} with profit {profit}")
        balance_over_time.append(balance)

    if position != 0:
        if position == 1:
            profit = (data.iloc[-1]['close'] - entry_price) * shares
            balance += shares * data.iloc[-1]['close']
            trades_df = record_trade(trades_df, ticker, data.index[-1], 'Long', 'Close', shares, data.iloc[-1]['close'], profit, balance)
            logging.debug(f"Final long position closed at price {data.iloc[-1]['close']} with profit {profit}")
        elif position == -1:
            profit = (entry_price - data.iloc[-1]['close']) * shares
            balance -= shares * data.iloc[-1]['close']
            trades_df = record_trade(trades_df, ticker, data.index[-1], 'Short', 'Close', shares, data.iloc[-1]['close'], profit, balance)
            logging.debug(f"Final short position closed at price {data.iloc[-1]['close']} with profit {profit}")

    logging.debug(f"Completed backtest for {ticker} on interval {interval}. Final balance: {balance}")
    return balance, balance_over_time, trades_df


def analyze_stocks(tickers, data_directory, strategy_name, strategy_func):
    logging.debug(f"Starting analysis for strategy: {strategy_name}")
    results = {}

    for interval in INTERVALS:
        interval_results = {}
        for ticker in tickers:
            file_path = os.path.join(data_directory, interval, f"{ticker}_{interval}.csv")
            if not os.path.exists(file_path):
                logging.warning(f"File not found: {file_path}. Skipping.")
                continue

            data = pd.read_csv(file_path, index_col=0, parse_dates=True)
            data = data.rename(columns=str.lower)
            if 'close' not in data.columns:
                logging.warning(f"Data for {ticker} ({interval}) does not contain 'close' column. Skipping this file.")
                continue

            data['close'] = pd.to_numeric(data['close'], errors='coerce')
            data = data.dropna(subset=['close'])
            if len(data) < 55:
                logging.warning(f"Not enough data for {ticker} ({interval}). Skipping.")
                continue

            logging.debug(f"Data for {ticker} ({interval}): {data.head()}")
            if strategy_name == "trendlines_with_breaks":
                final_balance, balance_over_time, trades_df = backtest(data, ticker, interval, strategy_func, {'ticker': ticker, 'interval': interval}, initial_balance=INITIAL_BALANCE)
            else:
                final_balance, balance_over_time, trades_df = backtest(data, ticker, interval, strategy_func, {}, initial_balance=INITIAL_BALANCE)
            
            interval_results[(ticker, interval)] = {
                "Final Balance": final_balance,
                "Balance Over Time": balance_over_time,
                "Profit": final_balance - INITIAL_BALANCE,
                "Profit Percentage": (final_balance / INITIAL_BALANCE - 1) * 100
            }

            output_dir = os.path.join(data_directory, 'strategy_results', strategy_name, interval, 'output')
            os.makedirs(output_dir, exist_ok=True)
            trades_file = os.path.join(output_dir, f"trades_{interval}.csv")
            if os.path.exists(trades_file):
                existing_trades = pd.read_csv(trades_file)
                trades_df = pd.concat([existing_trades, trades_df], ignore_index=True)
                trades_df = trades_df.drop_duplicates(subset=['Ticker', 'Date', 'Trade Type', 'Action', 'Shares', 'Price'])

            trades_df.to_csv(trades_file, index=False)
            logging.debug(f"Saved trades for {ticker} ({interval}) to {trades_file}")

        results.update(interval_results)

    logging.debug(f"Completed analysis for strategy: {strategy_name}")
    return results
