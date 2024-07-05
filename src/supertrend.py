import pandas as pd
import numpy as np
import talib

def supertrend(df, period, atr_multiplier):
    atr = talib.ATR(df['high'], df['low'], df['close'], timeperiod=period)
    hl2 = (df['high'] + df['low']) / 2
    final_upperband = hl2 + (atr_multiplier * atr)
    final_lowerband = hl2 - (atr_multiplier * atr)
    
    supertrend = [True] * len(df)
    for i in range(1, len(df)):
        if df['close'].iloc[i] > final_upperband.iloc[i-1]:
            supertrend[i] = True
        elif df['close'].iloc[i] < final_lowerband.iloc[i-1]:
            supertrend[i] = False
        else:
            supertrend[i] = supertrend[i-1]
            if supertrend[i] and final_lowerband.iloc[i] < final_lowerband.iloc[i-1]:
                final_lowerband.iloc[i] = final_lowerband.iloc[i-1]
            if not supertrend[i] and final_upperband.iloc[i] > final_upperband.iloc[i-1]:
                final_upperband.iloc[i] = final_upperband.iloc[i-1]
    
    df['supertrend'] = supertrend
    df['final_upperband'] = final_upperband
    df['final_lowerband'] = final_lowerband
    return df

def bollinger_bands(df, period=20, num_std_dev=2):
    df['middle_band'] = talib.SMA(df['close'], timeperiod=period)
    df['upper_band'], df['lower_band'], _ = talib.BBANDS(df['close'], timeperiod=period, nbdevup=num_std_dev, nbdevdn=num_std_dev, matype=0)
    return df

def strategy(data):
    data = data.rename(columns=str.lower)
    if 'close' not in data.columns:
        raise KeyError("DataFrame должен содержать столбец 'close'.")

    data['close'] = pd.to_numeric(data['close'], errors='coerce')
    data = data.dropna(subset=['close'])

    if len(data) < 55:
        print("Недостаточно данных для вычисления Supertrend и Bollinger Bands. Требуется как минимум 55 записей.")
        raise ValueError("Недостаточно данных для вычисления Supertrend и Bollinger Bands. Требуется как минимум 55 записей.")

    data = supertrend(data, period=12, atr_multiplier=3)
    data = bollinger_bands(data)

    # Generate Buy/Sell signals based on Supertrend and Bollinger Bands
    data['BuySignal'] = (data['supertrend'] & (data['close'] < data['lower_band'])).astype(int)
    data['SellSignal'] = (~data['supertrend'] & (data['close'] > data['upper_band'])).astype(int)

    return data
