from .base_strategy import BaseStrategy
from config.config import BOLLINGER_PERIOD, BOLLINGER_NUM_STD_DEV, SUPER_TREND_PERIOD, ATR_MULTIPLIER, SUPER_TREND_TAKE_PROFIT_PERCENT, SUPER_TREND_STOP_LOSS_PERCENT
import talib
import pandas as pd

def bollinger_bands(df, period=BOLLINGER_PERIOD, num_std_dev=BOLLINGER_NUM_STD_DEV):
    df['middle_band'] = talib.SMA(df['close'], timeperiod=period)
    df['upper_band'], df['lower_band'], _ = talib.BBANDS(df['close'], timeperiod=period, nbdevup=num_std_dev, nbdevdn=num_std_dev, matype=0)
    return df

def supertrend(df, period=SUPER_TREND_PERIOD, atr_multiplier=ATR_MULTIPLIER):
    atr = talib.ATR(df['high'], df['low'], df['close'], timeperiod=period)
    hl2 = (df['high'] + df['low']) / 2
    final_upperband = hl2 + (atr_multiplier * atr)
    final_lowerband = hl2 - (atr_multiplier * atr)
    
    supertrend = [True] * len(df)
    for i in range(1, len(df)):
        if df['close'].iloc[i] > final_upperband.iloc[i-1]:
            supertrend[i] = True
        elif df['close'].iloc[i] < final_lowerband.iloc[i-1]:
            supertrend[i] = False
        else:
            supertrend[i] = supertrend[i-1]
            if supertrend[i] and final_lowerband.iloc[i] < final_lowerband.iloc[i-1]:
                final_lowerband.iloc[i] = final_lowerband.iloc[i-1]
            if not supertrend[i] and final_upperband.iloc[i] > final_upperband.iloc[i-1]:
                final_upperband.iloc[i] = final_upperband.iloc[i-1]
    
    df['supertrend'] = supertrend
    df['final_upperband'] = final_upperband
    df['final_lowerband'] = final_lowerband
    return df

class SupertrendStrategy(BaseStrategy):
    def __init__(self, data, initial_balance, whole_shares_only=True):
        super().__init__(data, initial_balance, whole_shares_only)
        self.take_profit_percent = SUPER_TREND_TAKE_PROFIT_PERCENT
        self.stop_loss_percent = SUPER_TREND_STOP_LOSS_PERCENT

    def generate_signals(self):
        self.logger.info("Generating Supertrend and Bollinger Bands signals...")

        self.data.columns = map(str.lower, self.data.columns)
        required_columns = ['close', 'high', 'low']
        for col in required_columns:
            if (col not in self.data.columns):
                raise KeyError(f"DataFrame должен содержать столбец '{col}'.")

        self.data['close'] = pd.to_numeric(self.data['close'], errors='coerce')
        self.data = self.data.dropna(subset=['close'])

        if len(self.data) < max(BOLLINGER_PERIOD, SUPER_TREND_PERIOD):
            raise ValueError("Недостаточно данных для вычисления Supertrend и Bollinger Bands.")

        self.data = supertrend(self.data, period=SUPER_TREND_PERIOD, atr_multiplier=ATR_MULTIPLIER)
        self.data = bollinger_bands(self.data, period=BOLLINGER_PERIOD, num_std_dev=BOLLINGER_NUM_STD_DEV)

        self.data['in_flat'] = (self.data['close'] > self.data['lower_band']) & (self.data['close'] < self.data['upper_band'])

        signals = []
        for index, row in self.data.iterrows():
            if row['supertrend'] and (row['close'] < row['lower_band']) and not row['in_flat']:
                signals.append((index, 'buy'))
            elif not row['supertrend'] and (row['close'] > row['upper_band']) and not row['in_flat']:
                signals.append((index, 'sell'))

        self.logger.info(f"Generated {len(signals)} signals.")
        return signals

    def apply_stop_loss_and_take_profit(self, price, timestamp):
        """Применяет стоп-лосс и тейк-профит уровни для стратегии Supertrend"""
        if self.position > 0:
            entry_price = self.trades[-1]['Price']
            if self.position_type == 'Long':
                if price >= entry_price * (1 + self.take_profit_percent):
                    self.logger.info(f"Take profit triggered at {price} on {timestamp}")
                    self.close_position(price, timestamp, 'Long')
                elif price <= entry_price * (1 - self.stop_loss_percent):
                    self.logger.info(f"Stop loss triggered at {price} on {timestamp}")
                    self.close_position(price, timestamp, 'Long')
            elif self.position_type == 'Short':
                if price <= entry_price * (1 - self.take_profit_percent):
                    self.logger.info(f"Take profit triggered at {price} on {timestamp}")
                    self.close_position(price, timestamp, 'Short')
                elif price >= entry_price * (1 + self.stop_loss_percent):
                    self.logger.info(f"Stop loss triggered at {price} on {timestamp}")
                    self.close_position(price, timestamp, 'Short')

    def simulate_trading(self, signals):
        """Запускает симуляцию торговли на основе сгенерированных сигналов для Supertrend стратегии"""
        self.logger.info("Starting trade simulation for Supertrend Strategy...")
        position = 0
        balance = self.initial_balance
        shares = 0
        last_potential_trade = None
        entry_price = None

        for timestamp, signal in signals:
            price = self.data.loc[timestamp, 'close']
            
            if signal == 'buy':
                last_potential_trade = ('buy', price)
            elif signal == 'sell':
                last_potential_trade = ('sell', price)

            if last_potential_trade:
                trade_type, entry_price = last_potential_trade
                last_potential_trade = None
                if trade_type == 'buy' and position == 0:
                    position = 1
                    shares = balance // entry_price if self.whole_shares_only else balance / entry_price
                    balance -= shares * entry_price
                    self.record_trade(timestamp, 'Long', 'Open', shares, entry_price, 0, balance)
                elif trade_type == 'sell' and position == 0:
                    position = -1
                    shares = balance // entry_price if self.whole_shares_only else balance / entry_price
                    balance += shares * entry_price
                    self.record_trade(timestamp, 'Short', 'Open', shares, entry_price, 0, balance)

            if signal == 'sell' and position == 1:
                profit = (price - entry_price) * shares
                balance += shares * price
                self.record_trade(timestamp, 'Long', 'Close', shares, price, profit, balance)
                position = 0
            elif signal == 'buy' and position == -1:
                profit = (entry_price - price) * shares
                balance -= shares * price
                self.record_trade(timestamp, 'Short', 'Close', shares, price, profit, balance)
                position = 0
            elif position == 1:
                if price >= entry_price * (1 + self.take_profit_percent) or price <= entry_price * (1 - self.stop_loss_percent):
                    profit = (price - entry_price) * shares
                    balance += shares * price
                    self.record_trade(timestamp, 'Long', 'Close', shares, price, profit, balance)
                    position = 0
            elif position == -1:
                if price <= entry_price * (1 - self.take_profit_percent) or price >= entry_price * (1 + self.stop_loss_percent):
                    profit = (entry_price - price) * shares
                    balance -= shares * price
                    self.record_trade(timestamp, 'Short', 'Close', shares, price, profit, balance)
                    position = 0

        if position != 0:
            self.logger.info("Closing open position at the end of the period...")
            if position == 1:
                profit = (self.data.iloc[-1]['close'] - entry_price) * shares
                balance += shares * self.data.iloc[-1]['close']
                self.record_trade(self.data.index[-1], 'Long', 'Close', shares, self.data.iloc[-1]['close'], profit, balance)
            elif position == -1:
                profit = (entry_price - self.data.iloc[-1]['close']) * shares
                balance -= shares * self.data.iloc[-1]['close']
                self.record_trade(self.data.index[-1], 'Short', 'Close', shares, self.data.iloc[-1]['close'], profit, balance)

        results = {
            "initial_balance": self.initial_balance,
            "final_value": balance,
            "trades": self.trades
        }

        self.logger.info("Trade simulation for Supertrend Strategy completed.")
        return results
