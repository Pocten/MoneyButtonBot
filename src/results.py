import os
import pandas as pd
import logging
from config import TICKERS, DATA_DIRECTORY, INTERVALS, INITIAL_BALANCE
from download_data import get_company_info
from logging_setup import setup_logging

setup_logging('results.log')

def calculate_results(trades_df):
    logging.debug(f"Calculating results for trades dataframe")
    initial_balance = INITIAL_BALANCE
    final_balance = trades_df['Balance'].iloc[-1]
    profit = final_balance - initial_balance
    profit_percentage = (profit / initial_balance) * 100
    num_trades = len(trades_df)
    profitable_trades = trades_df[trades_df['Profit'] > 0]
    percentage_profitable_trades = (len(profitable_trades) / num_trades) * 100 if num_trades > 0 else 0

    return {
        "initial_balance": initial_balance,
        "final_balance": final_balance,
        "profit": profit,
        "profit_percentage": profit_percentage,
        "num_trades": num_trades,
        "percentage_profitable_trades": percentage_profitable_trades
    }

def generate_results_file(interval, trades_df, strategy_name):
    logging.debug(f"Generating results file for strategy {strategy_name} and interval {interval}")
    output_dir = os.path.join(DATA_DIRECTORY, 'strategy_results', strategy_name, interval, 'output')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"results_{interval}.txt")

    with open(output_file, 'w') as f:
        for ticker in TICKERS:
            ticker_trades = trades_df[trades_df['Ticker'] == ticker]
            if not ticker_trades.empty:
                company_info = get_company_info(ticker)
                results = calculate_results(ticker_trades)
                f.write("============================================\n")
                f.write(f"Full company name: {company_info['name']}\n")
                f.write(f"Ticker: {company_info['ticker']}\n")
                f.write(f"Company country: {company_info['country']}\n")
                f.write(f"Company exchange: {company_info['exchange']}\n")
                f.write("--------------------------------------------\n")
                f.write(f"Initial balance: {results['initial_balance']:.2f}$\n")
                f.write(f"Final Balance: {results['final_balance']:.2f}$\n")
                f.write("--------------------------------------------\n")
                f.write(f"Profit: {results['profit']:.2f}$\n")
                f.write(f"Profit Percentage: {results['profit_percentage']:.2f}%\n")
                f.write("--------------------------------------------\n")
                f.write(f"Number of trades: {results['num_trades']}\n")
                f.write(f"Percentage of profitable trades: {results['percentage_profitable_trades']:.2f}%\n")
                f.write("============================================\n")
    logging.debug(f"Results file generated at {output_file}")
