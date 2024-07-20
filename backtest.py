import importlib
from config.config import TICKERS, INTERVALS, INITIAL_BALANCE, TAKE_PROFIT_PERCENT, STOP_LOSS_PERCENT, WHOLE_SHARES_ONLY
from utils.data_loader import load_data
import logging

logger = logging.getLogger(__name__)

def backtest_strategy(strategy_class, ticker, interval):
    logger.info(f"Starting backtest for {strategy_class.__name__} on {ticker} with interval {interval}")
    data = load_data(ticker, interval)
    strategy = strategy_class(data)
    results = strategy.backtest(INITIAL_BALANCE, TAKE_PROFIT_PERCENT, STOP_LOSS_PERCENT, WHOLE_SHARES_ONLY)
    logger.info(f"Backtest for {strategy_class.__name__} on {ticker} with interval {interval} completed")
    return results

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    strategies = ["SupertrendStrategy", "TrendlinesWithBreaksStrategy"]
    for ticker in TICKERS:
        for interval in INTERVALS:
            for strategy_name in strategies:
                module = importlib.import_module(f'strategies.{strategy_name.lower()}')
                strategy_class = getattr(module, strategy_name)
                results = backtest_strategy(strategy_class, ticker, interval)
                print(f"Results for {strategy_name} on {ticker} with interval {interval}:")
                print(results)
