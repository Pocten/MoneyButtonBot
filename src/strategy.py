import talib
import pandas as pd
import numpy as np

def calculate_ema(data, periods):
    print(f"Calculating EMA with period {periods} for data length {len(data)}")
    if data.isnull().values.any():
        print("Data contains null values.")
    if not pd.api.types.is_numeric_dtype(data):
        print("Data contains non-numeric values.")
    if len(data) < periods:
        print(f"Not enough data points to calculate EMA with period {periods}.")
        raise ValueError(f"Not enough data points to calculate EMA with period {periods}.")
    if periods == 1:
        return data  # Возвращаем просто значения 'close'
    ema = talib.EMA(data.to_numpy(), timeperiod=periods)
    print(f"EMA calculated with period {periods}: {ema[:5]}")  # Печать первых значений EMA для отладки
    return ema

def strategy(data):
    data = data.rename(columns=str.lower)  # Приведение всех имен столбцов к нижнему регистру
    if 'close' not in data.columns:
        raise KeyError("DataFrame должен содержать столбец 'close'.")

    # Проверка, что столбец 'close' содержит числовые значения и нет пропущенных значений
    data['close'] = pd.to_numeric(data['close'], errors='coerce')
    data = data.dropna(subset=['close'])

    # Проверка длины данных
    if len(data) < 55:
        print("Недостаточно данных для вычисления EMA. Требуется как минимум 55 записей.")
        raise ValueError("Недостаточно данных для вычисления EMA. Требуется как минимум 55 записей.")

    print(data['close'].head())  # Печать первых значений столбца 'close' для отладки

    data['ema0'] = calculate_ema(data['close'], 1)
    data['ema1'] = calculate_ema(data['close'], 13)
    data['ema2'] = calculate_ema(data['close'], 21)
    data['ema3'] = calculate_ema(data['close'], 34)
    data['ema4'] = calculate_ema(data['close'], 55)

    # Убедимся, что нет NaN значений перед дальнейшими вычислениями
    data.dropna(subset=['ema1', 'ema2', 'ema3', 'ema4'], inplace=True)

    # Проверка, что столбцы EMA были добавлены
    print(data[['ema0', 'ema1', 'ema2', 'ema3', 'ema4']].head())

    data['Bull1'] = data['ema1'] < data['ema0']
    data['Bull2'] = data['ema2'] < data['ema0']
    data['Bull3'] = data['ema3'] < data['ema0']
    data['Bull4'] = data['ema4'] < data['ema0']

    data['BuySignal'] = data['Bull1'] & data['Bull2'] & data['Bull3'] & data['Bull4']
    data['SellSignal'] = ~(data['Bull1'] | data['Bull2'] | data['Bull3'] | data['Bull4'])

    return data
