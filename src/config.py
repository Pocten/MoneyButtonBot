TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "BABA", "V", "JNJ", "WMT", "NVDA"]
DATA_DIRECTORY = "data"

INTERVALS = {
    '1m': 7,
    '5m': 60,
    '15m': 60,
    '30m': 60,
    '1h': 730,
    '1d': None,
    '1wk': None,
    '1mo': None
}

# Trading parameters
INITIAL_BALANCE = 1000
TAKE_PROFIT_PERCENT = 0.20
STOP_LOSS_PERCENT = 0.10

BOLLINGER_PERIOD = 20
BOLLINGER_NUM_STD_DEV = 2

SUPER_TREND_PERIOD = 12
ATR_MULTIPLIER = 3

WHOLE_SHARES_ONLY = True  # True if only whole shares can be bought, False otherwise