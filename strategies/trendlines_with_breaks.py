from .base_strategy import BaseStrategy
import numpy as np
import pandas as pd
import talib
from config.config import TRENDLINES_LENGTH, TRENDLINES_MULTIPLIER, TRENDLINES_CALC_METHOD, TRENDLINES_BACKPAINT, TRENDLINES_TRAIL_PERCENT_TP, TRENDLINES_TRAIL_PERCENT_SL

class TrendlinesWithBreaksStrategy(BaseStrategy):
    def generate_signals(self):
        self.logger.info("Generating Trendlines with Breaks signals...")
        
        length = TRENDLINES_LENGTH
        mult = TRENDLINES_MULTIPLIER
        calcMethod = TRENDLINES_CALC_METHOD
        backpaint = TRENDLINES_BACKPAINT

        # Вычисление пиков и впадин
        self.data['ph'] = self.data['close'].rolling(window=length).apply(lambda x: x.argmax() == (len(x) - 1), raw=True)
        self.data['pl'] = self.data['close'].rolling(window=length).apply(lambda x: x.argmin() == (len(x) - 1), raw=True)

        # Функция для расчета наклона
        def calculate_slope(method, src, length, mult):
            if method == 'Atr':
                return talib.ATR(self.data['high'], self.data['low'], self.data['close'], timeperiod=length).iloc[-1] / length * mult
            elif method == 'Stdev':
                return self.data['close'].rolling(window=length).std().iloc[-1] / length * mult
            elif method == 'Linreg':
                n = np.arange(len(src))
                slope = (talib.SMA(src * n, timeperiod=length).iloc[-1] - talib.SMA(src, timeperiod=length).iloc[-1] * talib.SMA(n, timeperiod=length).iloc[-1]) / np.var(n) / 2 * mult
                return slope

        # Инициализация переменных
        self.data['upper'] = np.nan
        self.data['lower'] = np.nan
        self.data['slope_ph'] = np.nan
        self.data['slope_pl'] = np.nan

        signals = []
        upper = lower = slope_ph = slope_pl = 0.0

        for i in range(length, len(self.data)):
            if self.data['ph'].iloc[i]:
                slope_ph = calculate_slope(calcMethod, self.data['close'].iloc[i-length:i], length, mult)
                upper = self.data['close'].iloc[i]
            elif self.data['pl'].iloc[i]:
                slope_pl = calculate_slope(calcMethod, self.data['close'].iloc[i-length:i], length, mult)
                lower = self.data['close'].iloc[i]

            if self.data['ph'].iloc[i]:
                self.data.at[self.data.index[i], 'slope_ph'] = slope_ph
            elif self.data['pl'].iloc[i]:
                self.data.at[self.data.index[i], 'slope_pl'] = slope_pl

            if i > length:
                self.data.at[self.data.index[i], 'upper'] = upper - slope_ph * (i - length)
                self.data.at[self.data.index[i], 'lower'] = lower + slope_pl * (i - length)

        # Условия для открытия и закрытия позиций
        self.data['upos'] = np.where(self.data['close'] > self.data['upper'], 1, 0)
        self.data['dnos'] = np.where(self.data['close'] < self.data['lower'], 1, 0)

        # Генерация сигналов
        for i in range(1, len(self.data)):
            if self.data['upos'].iloc[i] > self.data['upos'].iloc[i - 1]:
                signals.append((self.data.index[i], 'buy'))
            elif self.data['dnos'].iloc[i] > self.data['dnos'].iloc[i - 1]:
                signals.append((self.data.index[i], 'sell'))

        self.logger.info(f"Generated {len(signals)} signals.")
        return signals

    def simulate_trading(self, signals):
        self.logger.info("Starting trade simulation for Trendlines with Breaks Strategy...")
        position = 0
        balance = self.initial_balance
        shares = 0
        entry_price = 0

        for timestamp, signal in signals:
            price = self.data.loc[timestamp, 'close']

            if signal == 'buy' and position == 0:
                shares = balance // price
                balance -= shares * price
                position = 1
                entry_price = price
                self.record_trade(timestamp, 'Long', 'Open', shares, price, 0, balance)
            elif signal == 'sell' and position == 1:
                balance += shares * price
                profit = (price - entry_price) * shares
                self.record_trade(timestamp, 'Long', 'Close', shares, price, profit, balance)
                position = 0

            if signal == 'sell' and position == 0:
                shares = balance // price
                balance += shares * price
                position = -1
                entry_price = price
                self.record_trade(timestamp, 'Short', 'Open', shares, price, 0, balance)
            elif signal == 'buy' and position == -1:
                balance -= shares * price
                profit = (entry_price - price) * shares
                self.record_trade(timestamp, 'Short', 'Close', shares, price, profit, balance)
                position = 0

            # Применение плавающего тейк-профита и стоп-лосса
            if position == 1:
                if price >= entry_price * (1 + TRENDLINES_TRAIL_PERCENT_TP / 100) or price <= entry_price * (1 - TRENDLINES_TRAIL_PERCENT_SL / 100):
                    balance += shares * price
                    profit = (price - entry_price) * shares
                    self.record_trade(timestamp, 'Long', 'Close', shares, price, profit, balance)
                    position = 0
            elif position == -1:
                if price <= entry_price * (1 - TRENDLINES_TRAIL_PERCENT_TP / 100) or price >= entry_price * (1 + TRENDLINES_TRAIL_PERCENT_SL / 100):
                    balance -= shares * price
                    profit = (entry_price - price) * shares
                    self.record_trade(timestamp, 'Short', 'Close', shares, price, profit, balance)
                    position = 0

        # Закрытие всех позиций в конце периода
        if position != 0:
            price = self.data['close'].iloc[-1]
            if position == 1:
                balance += shares * price
                profit = (price - entry_price) * shares
                self.record_trade(self.data.index[-1], 'Long', 'Close', shares, price, profit, balance)
            elif position == -1:
                balance -= shares * price
                profit = (entry_price - price) * shares
                self.record_trade(self.data.index[-1], 'Short', 'Close', shares, price, profit, balance)

        results = {
            "initial_balance": self.initial_balance,
            "final_value": balance,
            "trades": self.trades
        }

        self.logger.info("Trade simulation for Trendlines with Breaks Strategy completed.")
        return results
