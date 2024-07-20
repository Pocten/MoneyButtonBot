from .base_strategy import BaseStrategy
import talib
import pandas as pd

class SupertrendStrategy(BaseStrategy):
    def generate_signals(self):
        self.logger.info("Generating Supertrend signals...")
        factor1, length1 = 3.0, 12
        factor2, length2 = 1.0, 10
        factor3, length3 = 2.0, 11
        
        self.data['supertrend1'] = talib.SMA(self.data['Close'], timeperiod=length1)
        self.data['direction1'] = self.data['Close'] - self.data['supertrend1']
        self.data['supertrend2'] = talib.SMA(self.data['Close'], timeperiod=length2)
        self.data['direction2'] = self.data['Close'] - self.data['supertrend2']
        self.data['supertrend3'] = talib.SMA(self.data['Close'], timeperiod=length3)
        self.data['direction3'] = self.data['Close'] - self.data['supertrend3']

        signals = []
        for index, row in self.data.iterrows():
            same_color_long = (row['direction1'] < 0) and (row['direction2'] < 0) and (row['direction3'] < 0)
            same_color_short = (row['direction1'] > 0) and (row['direction2'] > 0) and (row['direction3'] > 0)

            if same_color_long:
                signals.append((index, 'buy'))
            elif same_color_short:
                signals.append((index, 'sell'))

        self.logger.info(f"Generated {len(signals)} signals.")
        return signals
