from .base_strategy import BaseStrategy
import numpy as np
import pandas as pd

class TrendlinesWithBreaksStrategy(BaseStrategy):
    def generate_signals(self):
        self.logger.info("Generating Trendlines with Breaks signals...")
        length = 18
        mult = 1.0
        
        self.data['ph'] = self.data['Close'].rolling(window=length).apply(lambda x: x.argmax() == (len(x) - 1), raw=True)
        self.data['pl'] = self.data['Close'].rolling(window=length).apply(lambda x: x.argmin() == (len(x) - 1), raw=True)

        signals = []
        for index, row in self.data.iterrows():
            if row['ph']:
                signals.append((index, 'short'))
            elif row['pl']:
                signals.append((index, 'cover'))

        self.logger.info(f"Generated {len(signals)} signals.")
        return signals
