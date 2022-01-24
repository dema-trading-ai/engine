import talib.abstract as ta
import pandas as pd
import numpy as np
import sys

from utils.error_handling import ErrorOutput, ModeNotAvailableError


def absolute_strength_histogram(dataframe, length=9, smooth=3, mode="RSI"):
    """
    Absolute Strenght Index. Returns smoothed bulls, smoothed bears, and difference
    :param dataframe: Dataframe with values
    :param length: Period of Evaluation
    :param smooth: Period of Smoothing
    :param mode: Indicator method. Choose from: ["RSI", "STOCHASTIC", "ADX"]
    :return:
    """

    df = dataframe.copy()

    try:

        if mode == "RSI":
            df['bulls'] = 0.5 * (abs(df['close'] - df['close'].shift(1)) + (df['close'] - df['close'].shift(1)))
            df['bears'] = 0.5 * (abs(df['close'] - df['close'].shift(1)) - (df['close'] - df['close'].shift(1)))

        elif mode == "STOCHASTIC":
            df['lowest_bars'] = df['close'].rolling(length).min()
            df['highest_bars'] = df['close'].rolling(length).max()

            df['bulls'] = df['close'] - df['lowest_bars']
            df['bears'] = df['highest_bars'] - df['close']

        elif mode == "ADX":
            df['bulls'] = 0.5 * (abs(df['high'] - df['high'].shift(1)) + (df['high'] - df['high'].shift(1)))
            df['bears'] = 0.5 * (abs(df['low'].shift(1) - df['low']) + (df['low'].shift(1) - df['low']))

        else:
            raise ModeNotAvailableError

    except ModeNotAvailableError:
        ErrorOutput(sys.exc_info(),
                    add_info="Mode not implemented yet, use RSI, STOCHASTIC or ADX.",
                    stop=True).print_error()

    df['avg_bulls'] = ta.EMA(df['bulls'], timeperiod=length)
    df['avg_bears'] = ta.EMA(df['bears'], timeperiod=length)

    df['smoothed_bulls'] = ta.EMA(df['avg_bulls'], timeperiod=smooth)
    df['smoothed_bears'] = ta.EMA(df['avg_bears'], timeperiod=smooth)

    df['difference'] = abs(df['smoothed_bulls'] - df['smoothed_bears'])

    return df['smoothed_bulls'], df['smoothed_bears'], df['difference']


def stoch_rsi(dataframe, period=14, smooth_d=3, smooth_k=3, rsi_period=14):
    """
    Returns the Stochastic RSI that replicates the TradingView's STOCHRSI
    :param dataframe: The dataframe
    :param period: rolling length
    :param smooth_d: Smoothing value
    :param smooth_k: Smoothing value
    :param rsi_period: Length of the RSI used.
    :return:
    """
    df = dataframe.copy()
    df['rsi'] = ta.RSI(df, timeperiod=rsi_period)
    stochrsi = (df['rsi'] - df['rsi'].rolling(period).min()) / (
                df['rsi'].rolling(period).max() - df['rsi'].rolling(period).min())
    df['srsi_k'] = stochrsi.rolling(smooth_k).mean() * 100
    df['srsi_d'] = df['srsi_k'].rolling(smooth_d).mean()
    return df['srsi_k'], df['srsi_d']


def VWMA(source, volume, length):
    """
    The vwma function returns volume-weighted moving average of 'source' for 'length' bars back.
    :param source: Prices to process
    :param volume: Volume
    :param length: Number of candles
    :return: VWMA
    """
    return ta.SMA(source * volume, length) / ta.SMA(volume, length)


def ichimoku_cloud(dataframe, conversion_length=9, base_line_length=26, lead_length=52, displacement=26):
    """
    Ichimoku Cloud, replicates TradingView version.
    :param dataframe: Dataframe
    :param conversion_length: Conversion Line Length
    :param base_line_length: Base Line Length
    :param lead_length: Lead Line Length
    :param displacement: The displacement
    :return: Conversion Line, Base Line, Lead Line 1, Lead Line 2
    """
    df = dataframe.copy()
    conversion_period_high = df['high'].rolling(conversion_length).max()
    conversion_period_low = df['low'].rolling(conversion_length).min()
    df['ichi_conversion'] = (conversion_period_high + conversion_period_low) / 2

    # Kijun-sen (Base Line): (x-period high + x-period low) / 2
    base_period_high = df['high'].rolling(base_line_length).max()
    base_period_low = df['low'].rolling(base_line_length).min()
    df['ichi_base_line'] = (base_period_high + base_period_low) / 2

    # Senkou Span A (Leading Span A): (Conversion Line + Base Line) / 2
    df['ichi_lead_line1'] = ((df['ichi_conversion'] + df['ichi_base_line']) / 2).shift(displacement - 1)

    # Senkou Span B (Leading Span B): (x-period high + x-period low) / 2
    lead_period_high = df['high'].rolling(lead_length).max()
    lead_period_low = df['low'].rolling(lead_length).min()
    df['ichi_lead_line2'] = ((lead_period_high + lead_period_low) / 2).shift(displacement - 1)

    return df['ichi_conversion'], df['ichi_base_line'], df['ichi_lead_line1'], df['ichi_lead_line2']


def heikin_dataframe(dataframe):
    """
    This function returns a dataframe with heikin ashi candles, based on the original dataframe passed to it as
    an argument
    :param dataframe: The original ohlcv candle dataframe
    :return: Heikin Ashi candle dataframe
    """
    # Heikin Open = (Open of Prev. Bar + Close of Prev. Bar) / 2
    dataframe['heikin_open'] = (dataframe['open'].shift(1) + dataframe['close'].shift(1)) / 2

    # Heikin Close = (Open + High + Low + Close) / 4
    dataframe['heikin_close'] = (dataframe['open'] + dataframe['high'] + dataframe['low'] + dataframe['close']) / 4

    # Heikin Low = Min[Low,  Open, Close] - (same as candlesticks)
    dataframe['heikin_low'] = dataframe['low']

    # Heikin high = Max[Low,  Open, Close] - (same as candlesticks)
    dataframe['heikin_high'] = dataframe['high']

    # Make a separate dict for the heikin values
    heikin_dict = {
        'open': dataframe['heikin_open'],
        'high': dataframe['heikin_high'],
        'low': dataframe['heikin_low'],
        'close': dataframe['heikin_close'],
        'volume': dataframe['volume']
    }

    heikin_dataframe = pd.DataFrame(heikin_dict)

    return heikin_dataframe


def HMA(dataframe, timeperiod):
    """
    This function returns the Hull Moving Average, calculated over the close values of a dataframe.
    Reference: https://github.com/DeviaVir/zenbot/issues/1426
    :param dataframe: The candle dataframe
    :param timeperiod: The timeperiod of the HMA
    :return: The Hull Moving Average
    """
    return ta.WMA(2 * ta.WMA(dataframe['close'], timeperiod // 2) - ta.WMA(dataframe['close'], timeperiod),
                  int(np.floor(np.sqrt(timeperiod))))
