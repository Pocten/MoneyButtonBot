import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio
import os
import logging
from config import TICKERS, DATA_DIRECTORY, INTERVALS, TRENDLINES_LOOKBACK, TRENDLINES_SLOPE_MULT
from logging_setup import setup_logging
from trendlines_with_breaks_strategy import identify_trendlines

setup_logging('plot_results.log')

def load_stock_data(tickers, data_directory, interval):
    logging.debug(f"Loading stock data for tickers: {tickers} with interval {interval}")
    stock_data = {}
    for ticker in tickers:
        file_path = os.path.join(data_directory, interval, f"{ticker}_{interval}.csv")
        if os.path.exists(file_path):
            logging.debug(f"Loading data from {file_path}")
            data = pd.read_csv(file_path, index_col=0, parse_dates=True)
            data.columns = data.columns.str.strip().str.lower()
            if 'close' not in data.columns:
                logging.warning(f"Data for {ticker} ({interval}) does not contain 'close' column. Skipping this file.")
                continue
            data.index = pd.to_datetime(data.index, utc=True)
            stock_data[ticker] = data
        else:
            logging.warning(f"File {file_path} does not exist. Skipping.")
    return stock_data

def create_price_plots(stock_data, trades_df, interval, strategy_name):
    logging.debug(f"Creating price plots for strategy {strategy_name} and interval {interval}")
    trades_df['Date'] = pd.to_datetime(trades_df['Date'], format='%d.%m.%Y %H:%M').dt.tz_localize('UTC')
    
    for ticker, data in stock_data.items():
        fig = go.Figure()

        trace_data = go.Scatter(x=data.index, y=data['close'], name=ticker, line=dict(color='blue'))
        fig.add_trace(trace_data)

        if strategy_name == "trendlines_with_breaks":
            high_trendlines, low_trendlines = identify_trendlines(data, lookback=TRENDLINES_LOOKBACK, slope_mult=TRENDLINES_SLOPE_MULT)
            for (start, end, line) in high_trendlines:
                fig.add_trace(go.Scatter(x=data.index[start:end+1], y=np.polyval(line, range(start, end+1)), mode='lines', name=f'{ticker} High Trendline'))
            for (start, end, line) in low_trendlines:
                fig.add_trace(go.Scatter(x=data.index[start:end+1], y=np.polyval(line, range(start, end+1)), mode='lines', name=f'{ticker} Low Trendline'))

        ticker_trades = trades_df[trades_df['Ticker'] == ticker]
        long_open = ticker_trades[(ticker_trades['Trade Type'] == 'Long') & (ticker_trades['Action'] == 'Open')]
        long_close = ticker_trades[(ticker_trades['Trade Type'] == 'Long') & (ticker_trades['Action'] == 'Close')]
        short_open = ticker_trades[(ticker_trades['Trade Type'] == 'Short') & (ticker_trades['Action'] == 'Open')]
        short_close = ticker_trades[(ticker_trades['Trade Type'] == 'Short') & (ticker_trades['Action'] == 'Close')]

        marker_size = 10 * 1.3  # Увеличение размера на 30%

        fig.add_trace(go.Scatter(x=long_open['Date'], y=long_open['Price'], mode='markers', marker_symbol='triangle-up', marker_color='green', marker_size=marker_size, name=f'{ticker} Long Open'))
        fig.add_trace(go.Scatter(x=long_close['Date'], y=long_close['Price'], mode='markers', marker_symbol='cross', marker_color='green', marker_size=marker_size, name=f'{ticker} Long Close'))
        fig.add_trace(go.Scatter(x=short_open['Date'], y=short_open['Price'], mode='markers', marker_symbol='triangle-down', marker_color='red', marker_size=marker_size, name=f'{ticker} Short Open'))
        fig.add_trace(go.Scatter(x=short_close['Date'], y=short_close['Price'], mode='markers', marker_symbol='cross', marker_color='red', marker_size=marker_size, name=f'{ticker} Short Close'))

        fig.update_layout(
            title=f"Price of {ticker} Over Time ({interval})",
            xaxis_title="Date",
            yaxis_title="Price"
        )

        plots_directory = os.path.join(DATA_DIRECTORY, 'strategy_results', strategy_name, interval, 'plots')
        os.makedirs(plots_directory, exist_ok=True)
        output_file = os.path.join(plots_directory, f"{ticker}_price_plot.html")
        pio.write_html(fig, file=output_file, auto_open=False)
        logging.debug(f"Saved price plot to {output_file}")
