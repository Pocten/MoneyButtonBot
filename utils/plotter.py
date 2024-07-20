import os
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import logging

logger = logging.getLogger(__name__)

def save_plot_as_html(data, signals, title, file_path):
    fig = go.Figure()

    trace_data = go.Scatter(x=data.index, y=data['Close'], name=title.split()[2], line=dict(color='blue'))
    fig.add_trace(trace_data)

    long_open = [signal for signal in signals if signal[1] == 'buy' and signal[2] == 'Long']
    long_close = [signal for signal in signals if signal[1] == 'sell' and signal[2] == 'Long']
    short_open = [signal for signal in signals if signal[1] == 'buy' and signal[2] == 'Short']
    short_close = [signal for signal in signals if signal[1] == 'sell' and signal[2] == 'Short']

    marker_size = 13

    fig.add_trace(go.Scatter(x=[signal[0] for signal in long_open], y=[data.loc[signal[0], 'Close'] for signal in long_open],
                             mode='markers', marker_symbol='triangle-up', marker_color='green', marker_size=marker_size, name='Long Open'))
    fig.add_trace(go.Scatter(x=[signal[0] for signal in long_close], y=[data.loc[signal[0], 'Close'] for signal in long_close],
                             mode='markers', marker_symbol='cross', marker_color='green', marker_size=marker_size, name='Long Close'))
    fig.add_trace(go.Scatter(x=[signal[0] for signal in short_open], y=[data.loc[signal[0], 'Close'] for signal in short_open],
                             mode='markers', marker_symbol='triangle-down', marker_color='red', marker_size=marker_size, name='Short Open'))
    fig.add_trace(go.Scatter(x=[signal[0] for signal in short_close], y=[data.loc[signal[0], 'Close'] for signal in short_close],
                             mode='markers', marker_symbol='cross', marker_color='red', marker_size=marker_size, name='Short Close'))

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Price"
    )

    pio.write_html(fig, file=file_path, auto_open=False)

def load_stock_data(tickers, data_directory, interval):
    stock_data = {}
    for ticker in tickers:
        file_path = os.path.join(data_directory, interval, f"{ticker}_{interval}.csv")
        if os.path.exists(file_path):
            data = pd.read_csv(file_path, index_col=0, parse_dates=True)
            data.columns = data.columns.str.strip().str.lower()
            if 'close' not in data.columns:
                continue
            data.index = pd.to_datetime(data.index, utc=True)
            stock_data[ticker] = data
    return stock_data

def create_price_plots(stock_data, trades_df, strategy_name, interval):
    try:
        if trades_df.empty:
            logger.error("Trades DataFrame is empty. Cannot create plots.")
            return

        if trades_df['Date'].str.contains('-').any():
            trades_df['Date'] = pd.to_datetime(trades_df['Date'], format='%d.%m.%Y %H:%M:%S%z', utc=True, dayfirst=True)
        else:
            trades_df['Date'] = pd.to_datetime(trades_df['Date'], format='%d.%m.%Y %H:%M:%S', dayfirst=True)
    except Exception as e:
        logger.error(f"Error parsing dates: {e}")
        return

    for ticker, data in stock_data.items():
        fig = go.Figure()

        trace_data = go.Scatter(x=data.index, y=data['close'], name=ticker, line=dict(color='blue'))
        fig.add_trace(trace_data)

        ticker_trades = trades_df[trades_df['Ticker'] == ticker]
        if ticker_trades.empty:
            logger.warning(f"No trades found for ticker {ticker}. Skipping plot.")
            continue

        long_open = ticker_trades[(ticker_trades['Trade Type'] == 'Long') & (ticker_trades['Action'] == 'Open')]
        long_close = ticker_trades[(ticker_trades['Trade Type'] == 'Long') & (ticker_trades['Action'] == 'Close')]
        short_open = ticker_trades[(ticker_trades['Trade Type'] == 'Short') & (ticker_trades['Action'] == 'Open')]
        short_close = ticker_trades[(ticker_trades['Trade Type'] == 'Short') & (ticker_trades['Action'] == 'Close')]

        marker_size = 13

        fig.add_trace(go.Scatter(x=long_open['Date'], y=long_open['Price'], mode='markers', marker_symbol='triangle-up', marker_color='green', marker_size=marker_size, name=f'{ticker} Long Open'))
        fig.add_trace(go.Scatter(x=long_close['Date'], y=long_close['Price'], mode='markers', marker_symbol='cross', marker_color='green', marker_size=marker_size, name=f'{ticker} Long Close'))
        fig.add_trace(go.Scatter(x=short_open['Date'], y=short_open['Price'], mode='markers', marker_symbol='triangle-down', marker_color='red', marker_size=marker_size, name=f'{ticker} Short Open'))
        fig.add_trace(go.Scatter(x=short_close['Date'], y=short_close['Price'], mode='markers', marker_symbol='cross', marker_color='red', marker_size=marker_size, name=f'{ticker} Short Close'))

        fig.update_layout(
            title=f"Price of {ticker} Over Time ({interval})",
            xaxis_title="Date",
            yaxis_title="Price"
        )

        plots_directory = os.path.join('data', 'results_of_strategies', strategy_name, interval, 'plots')
        os.makedirs(plots_directory, exist_ok=True)
        output_file = os.path.join(plots_directory, f"{ticker}_price_plot.html")
        pio.write_html(fig, file=output_file, auto_open=False)
