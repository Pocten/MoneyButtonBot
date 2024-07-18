import pandas as pd
import numpy as np
import talib
import logging
from config import SUPER_TREND_PERIOD, ATR_MULTIPLIER, BOLLINGER_PERIOD, BOLLINGER_NUM_STD_DEV
from logging_setup import setup_logging

setup_logging('supertrend.log')

def bollinger_bands(df, period=BOLLINGER_PERIOD, num_std_dev=BOLLINGER_NUM_STD_DEV):
    logging.debug(f"Calculating Bollinger Bands with period {period} and std dev {num_std_dev}")
    df['middle_band'] = talib.SMA(df['close'], timeperiod=period)
    df['upper_band'], df['lower_band'], _ = talib.BBANDS(df['close'], timeperiod=period, nbdevup=num_std_dev, nbdevdn=num_std_dev, matype=0)
    return df

def supertrend(df, period=SUPER_TREND_PERIOD, atr_multiplier=ATR_MULTIPLIER):
    logging.debug(f"Calculating Supertrend with period {period} and ATR multiplier {atr_multiplier}")
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

def strategy(data):  
    logging.debug("Executing Supertrend strategy")
    data = data.rename(columns=str.lower)
    if 'close' not in data.columns:
        logging.error("DataFrame должен содержать столбец 'close'.")
        raise KeyError("DataFrame должен содержать столбец 'close'.")

    data['close'] = pd.to_numeric(data['close'], errors='coerce')
    data = data.dropna(subset=['close'])

    if len(data) < 55:
        logging.error("Недостаточно данных для вычисления Supertrend и Bollinger Bands. Требуется как минимум 55 записей.")
        raise ValueError("Недостаточно данных для вычисления Supertrend и Bollinger Bands. Требуется как минимум 55 записей.")

    logging.debug("Calculating indicators")
    data = supertrend(data, period=SUPER_TREND_PERIOD, atr_multiplier=ATR_MULTIPLIER)
    data = bollinger_bands(data, period=BOLLINGER_PERIOD, num_std_dev=BOLLINGER_NUM_STD_DEV)
    
    # Определяем, когда рынок во флете
    data['in_flat'] = (data['close'] > data['lower_band']) & (data['close'] < data['upper_band'])
    
    # Генерация сигналов покупки и продажи
    data['BuySignal'] = (data['supertrend'] & (data['close'] < data['lower_band']) & ~data['in_flat']).astype(int)
    data['SellSignal'] = (~data['supertrend'] & (data['close'] > data['upper_band']) & ~data['in_flat']).astype(int)
    
    logging.debug(f"Buy signals generated: {data['BuySignal'].sum()}")
    logging.debug(f"Sell signals generated: {data['SellSignal'].sum()}")
    
    logging.debug("Supertrend strategy executed successfully")
    return data
