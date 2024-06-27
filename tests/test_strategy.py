import unittest
import pandas as pd
from src.strategy import strategy

class TestStrategy(unittest.TestCase):
    def test_strategy(self):
        data = pd.read_csv('data/historical/sample_data.csv')
        result = strategy(data)
        self.assertIn('BuySignal', result.columns)
        self.assertIn('SellSignal', result.columns)

if __name__ == '__main__':
    unittest.main()
