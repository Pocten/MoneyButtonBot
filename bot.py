import importlib
from config.config import TICKERS, INTERVALS, INITIAL_BALANCE, WHOLE_SHARES_ONLY
from utils.data_loader import download_all_data, load_data
from utils.logger import setup_logging
from utils.plotter import save_plot_as_html, load_stock_data, create_price_plots
from utils.results_saver import save_trade_results, save_summary_results
import logging
import os
import pandas as pd

def main():
    log_file = 'logs/bot.log'
    setup_logging(log_file)
    logger = logging.getLogger(__name__)

    logger.info("Starting data download...")
    download_all_data()
    logger.info("Data download completed.")

    strategies = {
        "supertrend": "SupertrendStrategy",
        "trendlines_with_breaks": "TrendlinesWithBreaksStrategy"
    }

    for strategy_name, strategy_class_name in strategies.items():
        for interval in INTERVALS:
            all_results = []

            for ticker in TICKERS:
                data = load_data(ticker, interval)
                if data is None or data.empty:
                    logger.warning(f"No data for {ticker} with interval {interval}, skipping...")
                    continue

                logger.info(f"Running backtest for {strategy_class_name} on {ticker} with interval {interval}...")
                module = importlib.import_module(f'strategies.{strategy_name}')
                strategy_class = getattr(module, strategy_class_name)
                strategy = strategy_class(data, INITIAL_BALANCE, WHOLE_SHARES_ONLY)
                results = strategy.backtest()
                logger.info(f"Results for {strategy_class_name} on {ticker} with interval {interval}: {results}")
                save_trade_results(strategy_name, ticker, interval, results)
                
                all_results.append((ticker, results))

            save_summary_results(all_results, strategy_name, interval)

            stock_data = load_stock_data(TICKERS, 'data/historical_data', interval)
            trades_df = pd.concat([pd.DataFrame(result['trades']) for _, result in all_results], ignore_index=True)
            trades_df['Ticker'] = [ticker for ticker, result in all_results for _ in result['trades']]
            create_price_plots(stock_data, trades_df, strategy_name, interval)

if __name__ == "__main__":
    main()
