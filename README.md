# MoneyButtonBot

MoneyButtonBot is an automated trading bot designed for TradingView and backtesting in Python. The bot uses multiple strategies to identify market trends and execute trades. Each strategy is maintained in a separate Git branch.

## Features

- **Multiple Strategies:** Includes various strategies such as Supertrend and EMA.
- **Bollinger Bands:** Uses Bollinger Bands to identify market conditions.
- **Automated Trading:** Places buy and sell orders based on conditions.
- **Risk Management:** Includes take profit and stop loss mechanisms.

## Branches and Strategies

Each strategy is implemented in a separate Git branch. To switch to a specific strategy, you need to checkout the corresponding branch.

### Available Strategies

- **EMA_Trend_Meter:** Uses Exponential Moving Averages for trading signals.
- **Combined_Supertrend_Strategy:** Combines Supertrend and Bollinger Bands for trading signals.

### Switching Between Strategies

To switch between strategies, use the following Git commands:

```sh
# Switch to EMA_Trend_Meter strategy
git checkout EMA_Trend_Meter

# Switch to Combined_Supertrend_Strategy strategy
git checkout Combined_Supertrend_Strategy
```
