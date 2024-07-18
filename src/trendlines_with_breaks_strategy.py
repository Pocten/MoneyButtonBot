import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import logging
from config import TRENDLINES_LOOKBACK, TRENDLINES_SLOPE_MULT, TRENDLINES_CALC_METHOD, TRENDLINES_BACKPAINT
from logging_setup import setup_logging

setup_logging('trendlines_with_breaks_strategy.log')

def identify_trendlines(data, lookback, slope_mult):
    logging.debug(f"Identifying trendlines with lookback {lookback} and slope multiplier {slope_mult}")
    highs = data['high'].values
    lows = data['low'].values

    high_peaks, _ = find_peaks(highs, distance=lookback)
    low_peaks, _ = find_peaks(-lows, distance=lookback)

    logging.debug(f"High peaks: {high_peaks}")
    logging.debug(f"Low peaks: {low_peaks}")

    high_trendlines = [(high_peaks[i], high_peaks[i+1], np.polyfit(range(high_peaks[i], high_peaks[i+1] + 1), highs[high_peaks[i]:high_peaks[i+1] + 1], 1)) for i in range(len(high_peaks) - 1)]
    low_trendlines = [(low_peaks[i], low_peaks[i+1], np.polyfit(range(low_peaks[i], low_peaks[i+1] + 1), lows[low_peaks[i]:low_peaks[i+1] + 1], 1)) for i in range(len(low_peaks) - 1)]

    logging.debug(f"High trendlines: {high_trendlines}")
    logging.debug(f"Low trendlines: {low_trendlines}")

    return high_trendlines, low_trendlines

def detect_breaks(data, trendlines):
    logging.debug("Detecting trendline breaks")
    breaks = []
    for (start, end, line) in trendlines:
        for i in range(start, end):
            close_price = data['close'].iloc[i]
            trendline_value = np.polyval(line, i)
            logging.debug(f"Checking break at {data.index[i]}: close price={close_price}, trendline value={trendline_value}")
            if close_price > trendline_value:
                breaks.append((data.index[i], 'buy'))
                logging.debug(f"Break detected at {data.index[i]}: 'buy'")
                break
            elif close_price < trendline_value:
                breaks.append((data.index[i], 'sell'))
                logging.debug(f"Break detected at {data.index[i]}: 'sell'")
                break
    return breaks

def trendlines_with_breaks_strategy(data, lookback=TRENDLINES_LOOKBACK, slope_mult=TRENDLINES_SLOPE_MULT):
    logging.debug("Executing trendlines with breaks strategy")
    if len(data) < lookback:
        logging.error("Недостаточно данных для анализа")
        print("Недостаточно данных для анализа")
        return data

    high_trendlines, low_trendlines = identify_trendlines(data, lookback, slope_mult)
    
    buy_signals = []
    sell_signals = []

    high_breaks = detect_breaks(data, high_trendlines)
    low_breaks = detect_breaks(data, low_trendlines)

    for break_date, signal in high_breaks + low_breaks:
        if signal == 'buy':
            buy_signals.append(break_date)
            logging.debug(f"Buy signal added for {break_date}")
        elif signal == 'sell':
            sell_signals.append(break_date)
            logging.debug(f"Sell signal added for {break_date}")

    logging.debug(f"Buy signals: {buy_signals}")
    logging.debug(f"Sell signals: {sell_signals}")

    data['BuySignal'] = data.index.isin(buy_signals).astype(int)
    data['SellSignal'] = data.index.isin(sell_signals).astype(int)
    data['in_flat'] = 0

    logging.debug("Trendlines with breaks strategy executed successfully")
    return data
