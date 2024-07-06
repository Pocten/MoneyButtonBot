import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.io as pio
import os
from config import TICKERS, DATA_DIRECTORY

# Функция для загрузки данных акций
def load_stock_data(tickers, data_directory):
    stock_data = {}
    for ticker in tickers:
        file_path = os.path.join(data_directory, f"{ticker}_hourly.csv")
        stock_data[ticker] = pd.read_csv(file_path, index_col=0, parse_dates=True).rename(columns=str.lower)
    return stock_data

# Функция для создания графиков для каждого тикера
def create_price_plots(stock_data):
    fig = make_subplots(rows=1, cols=1)
    dropdown_buttons = []

    for ticker in stock_data:
        data = stock_data[ticker]

        trace_data = go.Scatter(x=data.index, y=data['close'], name=ticker, visible=False, line=dict(color='blue'))
        fig.add_trace(trace_data, row=1, col=1)

        dropdown_buttons.append(
            dict(
                label=ticker,
                method="update",
                args=[{"visible": [ticker == t for t in stock_data]},
                      {"title": f"Price of {ticker} Over Time"}]
            )
        )

    # Установим видимость первого графика
    if stock_data:
        fig.data[0].visible = True

    fig.update_layout(
        updatemenus=[
            dict(
                active=0,
                buttons=dropdown_buttons
            )
        ]
    )

    fig.update_xaxes(
        tickformat="%Y-%m",
        dtick="M1",
        ticks="inside",
        tickangle=45
    )

    fig.update_layout(title="Price of Stocks Over Time", xaxis_title="Date", yaxis_title="Price")
    pio.show(fig)
