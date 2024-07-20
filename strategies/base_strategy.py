import logging
import pandas as pd

class BaseStrategy:
    def __init__(self, data, initial_balance, take_profit_percent, stop_loss_percent, whole_shares_only=True):
        self.data = data
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.take_profit_percent = take_profit_percent
        self.stop_loss_percent = stop_loss_percent
        self.whole_shares_only = whole_shares_only
        self.position = 0  # Количество акций в текущей позиции
        self.position_type = None  # Тип позиции: Long или Short
        self.trades = []  # Список сделок
        self.logger = logging.getLogger(self.__class__.__name__)

    def generate_signals(self):
        raise NotImplementedError("Should implement generate_signals()")

    def backtest(self):
        self.logger.info("Starting backtest...")
        signals = self.generate_signals()
        results = self.simulate_trading(signals)
        self.logger.info("Backtest completed.")
        return results

    def simulate_trading(self, signals):
        self.logger.info("Starting trade simulation...")
        
        for timestamp, signal in signals:
            price = self.data.loc[timestamp, 'Close']
            if signal == 'buy':
                self.buy(price, timestamp, 'Long')
            elif signal == 'sell':
                self.sell(price, timestamp, 'Long')
            elif signal == 'short':
                self.buy(price, timestamp, 'Short')
            elif signal == 'cover':
                self.sell(price, timestamp, 'Short')
            self.apply_stop_loss_and_take_profit(price, timestamp)

        results = {
            "initial_balance": self.initial_balance,
            "final_value": self.balance + self.position * self.data.iloc[-1]['Close'] * (1 if self.position_type == 'Long' else -1),
            "trades": self.trades
        }

        self.logger.info("Trade simulation completed.")
        return results

    def buy(self, price, timestamp, trade_type):
        if self.position_type == trade_type:
            self.logger.info(f"Already in a {trade_type} position, ignoring buy signal.")
            return
        
        shares_to_buy = self.balance // price if self.whole_shares_only else self.balance / price
        if shares_to_buy > 0:
            cost = shares_to_buy * price
            self.position += shares_to_buy
            self.balance -= cost
            trade = {
                'Date': timestamp.strftime('%d.%m.%Y %H:%M:%S%z'),
                'Trade Type': trade_type,
                'Action': 'Open',
                'Shares': shares_to_buy,
                'Price': price,
                'Profit': 0.0,
                'Balance': self.balance
            }
            self.trades.append(trade)
            self.position_type = trade_type
            self.logger.info(f"{trade['Action']} {shares_to_buy} shares at {price} on {timestamp}")

    def sell(self, price, timestamp, trade_type):
        if self.position == 0 or self.position_type != trade_type:
            self.logger.info(f"No {trade_type} position to sell, ignoring sell signal.")
            return
        
        proceeds = self.position * price
        profit = (proceeds - sum(trade['Shares'] * trade['Price'] for trade in self.trades if trade['Action'] == 'Open')) * (1 if trade_type == 'Long' else -1)
        self.balance += proceeds
        trade = {
            'Date': timestamp.strftime('%d.%m.%Y %H:%M:%S%z'),
            'Trade Type': trade_type,
            'Action': 'Close',
            'Shares': self.position,
            'Price': price,
            'Profit': profit,
            'Balance': self.balance
        }
        self.trades.append(trade)
        self.position = 0
        self.position_type = None
        self.logger.info(f"{trade['Action']} {self.position} shares at {price} on {timestamp}")

    def apply_stop_loss_and_take_profit(self, price, timestamp):
        if self.position > 0:
            entry_price = self.trades[-1]['Price']
            if self.position_type == 'Long':
                if price >= entry_price * (1 + self.take_profit_percent):
                    self.logger.info(f"Take profit triggered at {price} on {timestamp}")
                    self.sell(price, timestamp, 'Long')
                elif price <= entry_price * (1 - self.stop_loss_percent):
                    self.logger.info(f"Stop loss triggered at {price} on {timestamp}")
                    self.sell(price, timestamp, 'Long')
            elif self.position_type == 'Short':
                if price <= entry_price * (1 - self.take_profit_percent):
                    self.logger.info(f"Take profit triggered at {price} on {timestamp}")
                    self.sell(price, timestamp, 'Short')
                elif price >= entry_price * (1 + self.stop_loss_percent):
                    self.logger.info(f"Stop loss triggered at {price} on {timestamp}")
                    self.sell(price, timestamp, 'Short')
