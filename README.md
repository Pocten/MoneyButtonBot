MoneyButtonBot is an automated trading bot using the EMA (Exponential Moving Averages) strategy to identify market trends and execute trades.

## Features

- **EMA Indicators:** Uses multiple EMAs to identify bullish and bearish trends.
- **Automated Trading:** Places buy and sell orders based on EMA conditions.
- **Risk Management:** Includes take profit and stop loss mechanisms.

## Usage

1. Clone the repository:
    \`\`\`sh
    git clone https://github.com/yourusername/MoneyButtonBot.git
    cd MoneyButtonBot
    \`\`\`

2. Install the required dependencies:
    \`\`\`sh
    pip install -r requirements.txt
    \`\`\`

3. Ensure you are on the correct branch:
    \`\`\`sh
    git checkout EMA_Trend_Meter
    \`\`\`

4. Run the bot:
    \`\`\`sh
    python bot.py
    \`\`\`

## Requirements

- Python 3.x
- Pandas
- NumPy
- Matplotlib
- TA-Lib
- yfinance