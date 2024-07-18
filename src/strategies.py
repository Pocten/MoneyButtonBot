import logging
from supertrend import strategy as supertrend_strategy
from trendlines_with_breaks_strategy import trendlines_with_breaks_strategy
from logging_setup import setup_logging

setup_logging('strategies.log')

logging.debug("Loading trading strategies")

strategies = {
    "supertrend": supertrend_strategy,
    "trendlines_with_breaks": trendlines_with_breaks_strategy,
}

logging.debug("Trading strategies loaded successfully")
