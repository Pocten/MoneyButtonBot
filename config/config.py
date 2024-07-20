TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'BABA', 'V', 'JNJ', 'WMT', 'NVDA']

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

# Общие параметры
INITIAL_BALANCE = 1000 # Начальный баланс в долларах
WHOLE_SHARES_ONLY = True # Только целые акции (True) или доли акций (False)

# Параметры для стратегии Supertrend
BOLLINGER_PERIOD = 20 # Период для расчета Bollinger Bands
BOLLINGER_NUM_STD_DEV = 2 # Количество стандартных отклонений для Bollinger Bands
SUPER_TREND_PERIOD = 10 # Период для расчета Supertrend
ATR_MULTIPLIER = 3 # Множитель для ATR
SUPER_TREND_TAKE_PROFIT_PERCENT = 0.20 # 20% Take Profit
SUPER_TREND_STOP_LOSS_PERCENT = 0.10 # 10% Stop Loss

# Параметры для стратегии Trendlines with Breaks
TRENDLINES_LENGTH = 18 # Длина для расчета пиков и впадин
TRENDLINES_MULTIPLIER = 1.0 # Множитель для расчета наклона
TRENDLINES_CALC_METHOD = 'Atr'  # Опции: 'Atr', 'Stdev', 'Linreg'
TRENDLINES_BACKPAINT = True # Раскрашивать ли линии в прошлом
TRENDLINES_TRAIL_PERCENT_TP = 5.0  # 5% Take Profit
TRENDLINES_TRAIL_PERCENT_SL = 3.0  # 3% Stop Loss