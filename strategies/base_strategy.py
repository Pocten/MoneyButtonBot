import logging
import pandas as pd

class BaseStrategy:
    def __init__(self, data, initial_balance, whole_shares_only=True):
        self.data = data
        self.initial_balance = initial_balance
        self.balance = initial_balance
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

    def record_trade(self, timestamp, trade_type, action, shares, price, profit, balance):
        """Записывает сделку в журнал"""
        trade = {
            'Date': timestamp.strftime('%d.%m.%Y %H:%M:%S%z'),
            'Trade Type': trade_type,
            'Action': action,
            'Shares': shares,
            'Price': price,
            'Profit': profit,
            'Balance': balance
        }
        self.trades.append(trade)
        self.logger.info(f"{action} {shares} shares at {price} on {timestamp} as {trade_type} with profit {profit} and balance {balance}")
    
    def simulate_trading(self, signals):
        """Запускает симуляцию торговли на основе сгенерированных сигналов"""
        self.logger.info("Starting trade simulation...")
        for timestamp, signal in signals:
            price = self.data.loc[timestamp, 'close']
            if signal == 'buy':
                self.open_position(price, timestamp, 'Long')
            elif signal == 'sell':
                self.close_position(price, timestamp, 'Long')
            elif signal == 'short':
                self.open_position(price, timestamp, 'Short')
            elif signal == 'cover':
                self.close_position(price, timestamp, 'Short')
            self.apply_stop_loss_and_take_profit(price, timestamp)

        # Закрытие всех открытых позиций в конце периода
        if self.position != 0:
            self.logger.info("Closing open position at the end of the period...")
            self.close_position(self.data.iloc[-1]['close'], self.data.index[-1], self.position_type)

        results = {
            "initial_balance": self.initial_balance,
            "final_value": self.balance + self.position * self.data.iloc[-1]['close'] * (1 if self.position_type == 'Long' else -1),
            "trades": self.trades
        }

        self.logger.info("Trade simulation completed.")
        return results

    def open_position(self, price, timestamp, trade_type):
        """Открывает новую позицию"""
        if self.position_type == trade_type:
            self.logger.info(f"Already in a {trade_type} position, ignoring open signal.")
            return
        
        shares_to_trade = self.balance // price if self.whole_shares_only else self.balance / price
        if shares_to_trade > 0:
            cost = shares_to_trade * price
            if trade_type == 'Long':
                self.position += shares_to_trade
                self.balance -= cost
            else:  # Short
                self.position -= shares_to_trade
                self.balance += cost
            self.record_trade(timestamp, trade_type, 'Open', shares_to_trade, price, 0.0, self.balance)
            self.position_type = trade_type

    def close_position(self, price, timestamp, trade_type):
        """Закрывает существующую позицию"""
        if self.position == 0 or self.position_type != trade_type:
            self.logger.info(f"No {trade_type} position to close, ignoring close signal.")
            return
        
        proceeds = abs(self.position) * price
        profit = (proceeds - sum(trade['Shares'] * trade['Price'] for trade in self.trades if trade['Action'] == 'Open')) * (1 if trade_type == 'Long' else -1)
        if trade_type == 'Long':
            self.balance += proceeds
        else:  # Short
            self.balance -= proceeds
        self.record_trade(timestamp, trade_type, 'Close', abs(self.position), price, profit, self.balance)
        self.position = 0
        self.position_type = None

    def apply_stop_loss_and_take_profit(self, price, timestamp):
        """Применяет стоп-лосс и тейк-профит уровни. Может быть переопределен в дочерних классах."""
        pass  # В базовом классе этот метод не делает ничего, может быть переопределен в стратегиях
