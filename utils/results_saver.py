import os
import pandas as pd
import logging
import yfinance as yf

logger = logging.getLogger(__name__)

def save_trade_results(strategy_name, ticker, interval, results):
    directory = os.path.join('data', 'results_of_strategies', strategy_name, interval, 'trades')
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, f"{ticker}_trades.csv")
    
    trades_df = pd.DataFrame(results['trades'])
    trades_df.to_csv(file_path, index=False)
    logger.info(f"Trade results for {ticker} saved to {file_path}")

def get_company_info(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "name": info.get("longName", "N/A"),
        "ticker": ticker,
        "country": info.get("country", "N/A"),
        "exchange": info.get("exchange", "N/A")
    }

def calculate_results(trades_df):
    initial_balance = trades_df['Balance'].iloc[0]
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

def save_summary_results(all_results, strategy_name, interval):
    directory = os.path.join('data', 'results_of_strategies', strategy_name, interval)
    os.makedirs(directory, exist_ok=True)
    summary_file = os.path.join(directory, 'results.txt')
    
    all_results.sort(key=lambda x: x[1]['final_value'] / x[1]['initial_balance'], reverse=True)

    with open(summary_file, 'w') as f:
        for ticker, results in all_results:
            company_info = get_company_info(ticker)
            results_summary = calculate_results(pd.DataFrame(results['trades']))
            f.write("============================================\n")
            f.write(f"Full company name: {company_info['name']}\n")
            f.write(f"Ticker: {company_info['ticker']}\n")
            f.write(f"Company country: {company_info['country']}\n")
            f.write(f"Company exchange: {company_info['exchange']}\n")
            f.write("--------------------------------------------\n")
            f.write(f"Initial balance: {results_summary['initial_balance']:.2f}$\n")
            f.write(f"Final Balance: {results_summary['final_balance']:.2f}$\n")
            f.write("--------------------------------------------\n")
            f.write(f"Profit: {results_summary['profit']:.2f}$\n")
            f.write(f"Profit Percentage: {results_summary['profit_percentage']:.2f}%\n")
            f.write("--------------------------------------------\n")
            f.write(f"Number of trades: {results_summary['num_trades']}\n")
            f.write(f"Percentage of profitable trades: {results_summary['percentage_profitable_trades']:.2f}%\n")
            f.write("============================================\n\n")
    
    logger.info(f"Summary results saved to {summary_file}")
