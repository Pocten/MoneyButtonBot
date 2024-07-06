import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio
import os
from config import TICKERS, DATA_DIRECTORY

# Загрузка данных акций
def load_stock_data(tickers, data_directory):
    stock_data = {}
    for ticker in tickers:
        file_path = os.path.join(data_directory, f"{ticker}_hourly.csv")
        stock_data[ticker] = pd.read_csv(file_path, index_col=0, parse_dates=True).rename(columns=str.lower)
    return stock_data

# Создание графиков для каждого тикера
def create_price_plots(stock_data, trades_df):
    # Создание папки plots, если ее нет
    plots_directory = os.path.join(DATA_DIRECTORY, "plots")
    os.makedirs(plots_directory, exist_ok=True)

    for ticker in stock_data:
        data = stock_data[ticker]
        fig = go.Figure()

        trace_data = go.Scatter(x=data.index, y=data['close'], name=ticker, line=dict(color='blue'))
        fig.add_trace(trace_data)

        # Добавление сделок
        ticker_trades = trades_df[trades_df['Ticker'] == ticker]
        long_open = ticker_trades[(ticker_trades['Trade Type'] == 'Long') & (ticker_trades['Action'] == 'Open')]
        long_close = ticker_trades[(ticker_trades['Trade Type'] == 'Long') & (ticker_trades['Action'] == 'Close')]
        short_open = ticker_trades[(ticker_trades['Trade Type'] == 'Short') & (ticker_trades['Action'] == 'Open')]
        short_close = ticker_trades[(ticker_trades['Trade Type'] == 'Short') & (ticker_trades['Action'] == 'Close')]

        marker_size = 10 * 1.2  # Увеличение размера на 20%

        fig.add_trace(go.Scatter(x=long_open['Date'], y=long_open['Price'], mode='markers', marker_symbol='triangle-up', marker_color='green', marker_size=marker_size, name=f'{ticker} Long Open'))
        fig.add_trace(go.Scatter(x=long_close['Date'], y=long_close['Price'], mode='markers', marker_symbol='cross', marker_color='green', marker_size=marker_size, name=f'{ticker} Long Close'))
        fig.add_trace(go.Scatter(x=short_open['Date'], y=short_open['Price'], mode='markers', marker_symbol='triangle-down', marker_color='red', marker_size=marker_size, name=f'{ticker} Short Open'))
        fig.add_trace(go.Scatter(x=short_close['Date'], y=short_close['Price'], mode='markers', marker_symbol='cross', marker_color='red', marker_size=marker_size, name=f'{ticker} Short Close'))

        fig.update_layout(
            title=f"Price of {ticker} Over Time",
            xaxis_title="Date",
            yaxis_title="Price"
        )

        # Сохранение графика в HTML файл
        output_file = os.path.join(plots_directory, f"{ticker}_price_plot.html")
        pio.write_html(fig, file=output_file, auto_open=True)

# Обновление bot.py для вызова create_price_plots
