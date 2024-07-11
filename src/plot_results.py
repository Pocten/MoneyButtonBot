import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio
import os
from config import TICKERS, DATA_DIRECTORY, INTERVALS

def load_stock_data(tickers, data_directory, interval):
    stock_data = {}
    for ticker in tickers:
        file_path = os.path.join(data_directory, interval, f"{ticker}_{interval}.csv")
        if os.path.exists(file_path):
            data = pd.read_csv(file_path, index_col=0, parse_dates=True)
            # Приводим все заголовки столбцов к нижнему регистру и убираем пробелы
            data.columns = data.columns.str.strip().str.lower()
            if 'close' not in data.columns:
                # print(f"Warning: 'close' column not found in file {file_path}. Skipping this file.")
                continue
            # Преобразование индекса
            data.index = pd.to_datetime(data.index, utc=True)
            stock_data[ticker] = data
            # print(f"Processing file: {file_path}")
    return stock_data

def create_price_plots(stock_data, trades_df, interval):
    trades_df['Date'] = pd.to_datetime(trades_df['Date'], format='%d.%m.%Y %H:%M').dt.tz_localize('UTC')
    
    for ticker, data in stock_data.items():
        fig = go.Figure()

        trace_data = go.Scatter(x=data.index, y=data['close'], name=ticker, line=dict(color='blue'))
        fig.add_trace(trace_data)

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

        # Сохранение графика в HTML файл
        plots_directory = os.path.join(DATA_DIRECTORY, interval, 'plots')
        os.makedirs(plots_directory, exist_ok=True)
        output_file = os.path.join(plots_directory, f"{ticker}_price_plot.html")
        pio.write_html(fig, file=output_file, auto_open=False)