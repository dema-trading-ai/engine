# Mandatory Imports
import talib.abstract as ta
from pandas import DataFrame
from backtesting.strategy import Strategy
from modules.setup.config import qtpylib_methods as qtpylib


class IndicatorSample(Strategy):
    """
    This is an example custom strategy, that inherits from the main Strategy class
    """

    def generate_indicators(self, dataframe: DataFrame) -> DataFrame:
        """
        :param dataframe: All passed candles (current candle included!) with OHLCV data
        :type dataframe: DataFrame
        :return: Dataframe filled with indicator-data
        :rtype: DataFrame
        """
        # RSI - Relative Strength Index
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # EMA - Exponential Moving Average
        dataframe['ema5'] = ta.EMA(dataframe, timeperiod=5)
        dataframe['ema21'] = ta.EMA(dataframe, timeperiod=21)

        # Momentum Indicators
        # ------------------------------------
        # ADX
        # dataframe['adx'] = ta.ADX(dataframe)

        # # Plus Directional Indicator / Movement
        # dataframe['plus_dm'] = ta.PLUS_DM(dataframe)
        # dataframe['plus_di'] = ta.PLUS_DI(dataframe)

        # # Minus Directional Indicator / Movement
        # dataframe['minus_dm'] = ta.MINUS_DM(dataframe)
        # dataframe['minus_di'] = ta.MINUS_DI(dataframe)

        # # Aroon, Aroon Oscillator
        # aroon = ta.AROON(dataframe)
        # dataframe['aroonup'] = aroon['aroonup']
        # dataframe['aroondown'] = aroon['aroondown']
        # dataframe['aroonosc'] = ta.AROONOSC(dataframe)

        # # Awesome Oscillator
        # dataframe['ao'] = qtpylib.awesome_oscillator(dataframe)

        # # Keltner Channel
        # keltner = qtpylib.keltner_channel(dataframe)
        # dataframe["kc_upperband"] = keltner["upper"]
        # dataframe["kc_lowerband"] = keltner["lower"]
        # dataframe["kc_middleband"] = keltner["mid"]
        # dataframe["kc_percent"] = (
        #     (dataframe["close"] - dataframe["kc_lowerband"]) /
        #     (dataframe["kc_upperband"] - dataframe["kc_lowerband"])
        # )
        # dataframe["kc_width"] = (
        #     (dataframe["kc_upperband"] - dataframe["kc_lowerband"]) / dataframe["kc_middleband"]
        # )

        # # Ultimate Oscillator
        # dataframe['uo'] = ta.ULTOSC(dataframe)

        # # Commodity Channel Index: values [Oversold:-100, Overbought:100]
        # dataframe['cci'] = ta.CCI(dataframe)

        # RSI
        # dataframe['rsi'] = ta.RSI(dataframe)

        # Absolute Strength Histogram
        # def absolute_strength_histogram(dataframe, length=9, smooth=3, mode="RSI"):
        #     """
        #     Absolute Strenght Index. Returns smoothed bulls, smoothed bears, and difference
        #     :param dataframe: Dataframe with values
        #     :param length: Period of Evaluation
        #     :param smooth: Period of Smoothing
        #     :param mode: Indicator method. Choose from: ["RSI", "STOCHASTIC", "ADX"]
        #     :return:
        #     """
        #     df = dataframe.copy()
        #
        #     if mode == "RSI":
        #         df['bulls'] = 0.5 * (abs(df['close'] - df['close'].shift(1)) + (df['close'] - df['close'].shift(1)))
        #         df['bears'] = 0.5 * (abs(df['close'] - df['close'].shift(1)) - (df['close'] - df['close'].shift(1)))
        #
        #     elif mode == "STOCHASTIC":
        #         df['lowest_bars'] = df['close'].rolling(length).min()
        #         df['highest_bars'] = df['close'].rolling(length).max()
        #
        #         df['bulls'] = df['close'] - df['lowest_bars']
        #         df['bears'] = df['highest_bars'] - df['close']
        #
        #     elif mode == "ADX":
        #         df['bulls'] = 0.5 * (abs(df['high'] - df['high'].shift(1)) + (df['high'] - df['high'].shift(1)))
        #         df['bears'] = 0.5 * (abs(df['low'].shift(1) - df['low']) + (df['low'].shift(1) - df['low']))
        #     else:
        #         raise ValueError("Mode not implemented yet, use RSI, STOCHASTIC or ADX")
        #
        #     df['avg_bulls'] = ta.EMA(df['bulls'], timeperiod=length)
        #     df['avg_bears'] = ta.EMA(df['bears'], timeperiod=length)
        #
        #     df['smoothed_bulls'] = ta.EMA(df['avg_bulls'], timeperiod=smooth)
        #     df['smoothed_bears'] = ta.EMA(df['avg_bears'], timeperiod=smooth)
        #
        #     df['difference'] = abs(df['smoothed_bulls'] - df['smoothed_bears'])
        #
        #     return df['smoothed_bulls'], df['smoothed_bears'], df['difference']
        #
        # ash = absolute_strength_histogram(dataframe, length=9, smooth=3, mode="RSI")
        # dataframe['smth_bulls'] = ash[0]
        # dataframe['smth_bears'] = ash[1]
        # dataframe['difference'] = ash[2]

        # # Inverse Fisher transform on RSI: values [-1.0, 1.0] (https://goo.gl/2JGGoy)
        # rsi = 0.1 * (dataframe['rsi'] - 50)
        # dataframe['fisher_rsi'] = (np.exp(2 * rsi) - 1) / (np.exp(2 * rsi) + 1)

        # # Inverse Fisher transform on RSI normalized: values [0.0, 100.0] (https://goo.gl/2JGGoy)
        # dataframe['fisher_rsi_norma'] = 50 * (dataframe['fisher_rsi'] + 1)

        # # Stochastic Slow
        # stoch = ta.STOCH(dataframe)
        # dataframe['slowd'] = stoch['slowd']
        # dataframe['slowk'] = stoch['slowk']

        # Stochastic Fast
        # stoch_fast = ta.STOCHF(dataframe)
        # dataframe['fastd'] = stoch_fast['fastd']
        # dataframe['fastk'] = stoch_fast['fastk']

        # # Stochastic RSI
        # STOCHRSI is NOT aligned with tradingview, which may result in non-expected results.
        # stoch_rsi = ta.STOCHRSI(dataframe)
        # dataframe['fastd_rsi'] = stoch_rsi['fastd']
        # dataframe['fastk_rsi'] = stoch_rsi['fastk']

        # # Stochastic RSI (Different implementation that corresponds with TradingView
        # def stoch_rsi(dataframe, period=14, smoothD=3, smoothK=3, rsi_period=14):
        #     """
        #     Returns the Stochastic RSI that replicates the TradingView's STOCHRSI
        #     :param dataframe: The dataframe
        #     :param period: rolling length
        #     :param smoothD: Smoothing value
        #     :param smoothK: Smoothing value
        #     :param rsi_period: Length of the RSI used.
        #     :return:
        #     """
        #     df = dataframe.copy()
        #     df['rsi'] = ta.RSI(df, timeperiod=rsi_period)
        #     stochrsi = (df['rsi'] - df['rsi'].rolling(period).min()) / (df['rsi'].rolling(period).max() - df['rsi'].rolling(period).min())
        #     df['srsi_k'] = stochrsi.rolling(smoothK).mean() * 100
        #     df['srsi_d'] = df['srsi_k'].rolling(smoothD).mean()
        #     return df['srsi_k'], df['srsi_d']
        #
        # stoch_rsi = stoch_rsi(dataframe, period=14, smoothD=3, smoothK=3, rsi_period=14)
        # dataframe['srsi_k'] = stoch_rsi[0]
        # dataframe['srsi_d'] = stoch_rsi[1]

        # MACD
        # macd = ta.MACD(dataframe)
        # dataframe['macd'] = macd['macd']
        # dataframe['macdsignal'] = macd['macdsignal']
        # dataframe['macdhist'] = macd['macdhist']

        # MFI
        # dataframe['mfi'] = ta.MFI(dataframe)

        # # ROC
        # dataframe['roc'] = ta.ROC(dataframe)

        # Overlap Studies

        # Rolling VWAP
        # dataframe['rvwap'] = qtpylib.rolling_vwap(dataframe, window=200)

        # def VWMA(source, volume, length):
        #     """
        #     The vwma function returns volume-weighted moving average of 'source' for 'length' bars back.
        #     :param source: Prices to process
        #     :param volume: Volume
        #     :param length: Number of candles
        #     :return: VWMA
        #     """
        #     return ta.SMA(source * volume, length) / ta.SMA(volume, length)
        #
        # dataframe['vwma20'] = VWMA(dataframe['close'], dataframe['volume'], 20)

        # Bollinger Bands
        # bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        # dataframe['bb_lowerband'] = bollinger['lower']
        # dataframe['bb_middleband'] = bollinger['mid']
        # dataframe['bb_upperband'] = bollinger['upper']
        # dataframe["bb_percent"] = ((dataframe["close"] - dataframe["bb_lowerband"]) / (dataframe["bb_upperband"] - dataframe["bb_lowerband"]))
        # dataframe["bb_width"] = ((dataframe["bb_upperband"] - dataframe["bb_lowerband"]) / dataframe["bb_middleband"])
        # Bollinger Bands - Weighted (EMA based instead of SMA)
        # weighted_bollinger = qtpylib.weighted_bollinger_bands(
        #     qtpylib.typical_price(dataframe), window=20, stds=2
        # )
        # dataframe["wbb_upperband"] = weighted_bollinger["upper"]
        # dataframe["wbb_lowerband"] = weighted_bollinger["lower"]
        # dataframe["wbb_middleband"] = weighted_bollinger["mid"]
        # dataframe["wbb_percent"] = (
        #     (dataframe["close"] - dataframe["wbb_lowerband"]) /
        #     (dataframe["wbb_upperband"] - dataframe["wbb_lowerband"])
        # )
        # dataframe["wbb_width"] = (
        #     (dataframe["wbb_upperband"] - dataframe["wbb_lowerband"]) /
        #     dataframe["wbb_middleband"]
        # )

        # # EMA - Exponential Moving Average
        # dataframe['ema3'] = ta.EMA(dataframe, timeperiod=3)
        # dataframe['ema5'] = ta.EMA(dataframe, timeperiod=5)
        # dataframe['ema10'] = ta.EMA(dataframe, timeperiod=10)
        # dataframe['ema21'] = ta.EMA(dataframe, timeperiod=21)
        # dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        # dataframe['ema100'] = ta.EMA(dataframe, timeperiod=100)

        # # SMA - Simple Moving Average
        # dataframe['sma3'] = ta.SMA(dataframe, timeperiod=3)
        # dataframe['sma5'] = ta.SMA(dataframe, timeperiod=5)
        # dataframe['sma10'] = ta.SMA(dataframe, timeperiod=10)
        # dataframe['sma21'] = ta.SMA(dataframe, timeperiod=21)
        # dataframe['sma50'] = ta.SMA(dataframe, timeperiod=50)
        # dataframe['sma100'] = ta.SMA(dataframe, timeperiod=100)

        # Parabolic SAR
        # dataframe['sar'] = ta.SAR(dataframe)

        # TEMA - Triple Exponential Moving Average
        # dataframe['tema'] = ta.TEMA(dataframe, timeperiod=21)

        # Hilbert Transform Indicator - SineWave
        # hilbert = ta.HT_SINE(dataframe)
        # dataframe['htsine'] = hilbert['sine']
        # dataframe['htleadsine'] = hilbert['leadsine']

        # Pattern Recognition - Bullish candlestick patterns
        # # Hammer: values [0, 100]
        # dataframe['CDLHAMMER'] = ta.CDLHAMMER(dataframe)

        # # Inverted Hammer: values [0, 100]
        # dataframe['CDLINVERTEDHAMMER'] = ta.CDLINVERTEDHAMMER(dataframe)

        # # Dragonfly Doji: values [0, 100]
        # dataframe['CDLDRAGONFLYDOJI'] = ta.CDLDRAGONFLYDOJI(dataframe)

        # # Piercing Line: values [0, 100]
        # dataframe['CDLPIERCING'] = ta.CDLPIERCING(dataframe) # values [0, 100]

        # # Morningstar: values [0, 100]
        # dataframe['CDLMORNINGSTAR'] = ta.CDLMORNINGSTAR(dataframe) # values [0, 100]

        # # Three White Soldiers: values [0, 100]
        # dataframe['CDL3WHITESOLDIERS'] = ta.CDL3WHITESOLDIERS(dataframe) # values [0, 100]
        # Pattern Recognition - Bearish candlestick patterns

        # # Hanging Man: values [0, 100]
        # dataframe['CDLHANGINGMAN'] = ta.CDLHANGINGMAN(dataframe)

        # # Shooting Star: values [0, 100]
        # dataframe['CDLSHOOTINGSTAR'] = ta.CDLSHOOTINGSTAR(dataframe)

        # # Gravestone Doji: values [0, 100]
        # dataframe['CDLGRAVESTONEDOJI'] = ta.CDLGRAVESTONEDOJI(dataframe)

        # # Dark Cloud Cover: values [0, 100]
        # dataframe['CDLDARKCLOUDCOVER'] = ta.CDLDARKCLOUDCOVER(dataframe)

        # # Evening Doji Star: values [0, 100]
        # dataframe['CDLEVENINGDOJISTAR'] = ta.CDLEVENINGDOJISTAR(dataframe)

        # # Evening Star: values [0, 100]
        # dataframe['CDLEVENINGSTAR'] = ta.CDLEVENINGSTAR(dataframe)

        # Pattern Recognition - Bullish/Bearish candlestick patterns
        # # Three Line Strike: values [0, -100, 100]
        # dataframe['CDL3LINESTRIKE'] = ta.CDL3LINESTRIKE(dataframe)

        # # Spinning Top: values [0, -100, 100]
        # dataframe['CDLSPINNINGTOP'] = ta.CDLSPINNINGTOP(dataframe) # values [0, -100, 100]

        # # Engulfing: values [0, -100, 100]
        # dataframe['CDLENGULFING'] = ta.CDLENGULFING(dataframe) # values [0, -100, 100]

        # # Harami: values [0, -100, 100]
        # dataframe['CDLHARAMI'] = ta.CDLHARAMI(dataframe) # values [0, -100, 100]

        # # Three Outside Up/Down: values [0, -100, 100]
        # dataframe['CDL3OUTSIDE'] = ta.CDL3OUTSIDE(dataframe) # values [0, -100, 100]

        # # Three Inside Up/Down: values [0, -100, 100]
        # dataframe['CDL3INSIDE'] = ta.CDL3INSIDE(dataframe) # values [0, -100, 100]

        # Ichimoku Cloud
        # def ichimoku_cloud(dataframe, conversion_length=9, base_line_length=26, lead_length=52, displacement=26):
        #     """
        #     Ichimoku Cloud, replicates TradingView version.
        #     :param dataframe: Dataframe
        #     :param conversion_length: Conversion Line Length
        #     :param base_line_length: Base Line Length
        #     :param lead_length: Lead Line Length
        #     :param displacement: The displacement
        #     :return: Conversion Line, Base Line, Lead Line 1, Lead Line 2
        #     """
        #     df = dataframe.copy()
        #     conversion_period_high = df['high'].rolling(conversion_length).max()
        #     conversion_period_low = df['low'].rolling(conversion_length).min()
        #     df['ichi_conversion'] = (conversion_period_high + conversion_period_low) / 2
        #
        #     # Kijun-sen (Base Line): (x-period high + x-period low) / 2
        #     base_period_high = df['high'].rolling(base_line_length).max()
        #     base_period_low = df['low'].rolling(base_line_length).min()
        #     df['ichi_base_line'] = (base_period_high + base_period_low) / 2
        #
        #     # Senkou Span A (Leading Span A): (Conversion Line + Base Line) / 2
        #     df['ichi_lead_line1'] = ((df['ichi_conversion'] + df['ichi_base_line']) / 2).shift(displacement - 1)
        #
        #     # Senkou Span B (Leading Span B): (x-period high + x-period low) / 2
        #     lead_period_high = df['high'].rolling(lead_length).max()
        #     lead_period_low = df['low'].rolling(lead_length).min()
        #     df['ichi_lead_line2'] = ((lead_period_high + lead_period_low) / 2).shift(displacement - 1)
        #
        #     return df['ichi_conversion'], df['ichi_base_line'], df['ichi_lead_line1'], df['ichi_lead_line2']
        #
        # ichimoku_cloud = ichimoku_cloud(dataframe, conversion_length=9, base_line_length=26, lead_length=52, displacement=26)
        # dataframe['ichi_conversion'] = ichimoku_cloud[0]
        # dataframe['ichi_base_line'] = ichimoku_cloud[1]
        # dataframe['ichi_lead_line1'] = ichimoku_cloud[2]
        # dataframe['ichi_lead_line2'] = ichimoku_cloud[3]

        return dataframe

    def buy_signal(self, dataframe: DataFrame) -> DataFrame:
        """
        :param dataframe: Dataframe filled with indicators from generate_indicators
        :type indicators: DataFrame
        :return: dataframe filled with buy signals
        :rtype: DataFrame
        """
        # BEGIN STRATEGY

        dataframe.loc[
            (
                (dataframe['rsi'] < 30) &
                (dataframe['ema5'] < dataframe['ema21']) &
                (dataframe['volume'] > 0)
            ),
            'buy'] = 1

        # END STRATEGY

        return dataframe

    def sell_signal(self, dataframe: DataFrame) -> DataFrame:
        """
        :param dataframe: Dataframe filled with indicators from generate_indicators
        :type indicators: DataFrame
        :return: dataframe filled with sell signals
        :rtype: DataFrame
        """
        # BEGIN STRATEGY

        dataframe.loc[
            (
                (dataframe['rsi'] > 70) &
                (dataframe['volume'] > 0)
            ),
            'sell'] = 1

        # END STRATEGY

        return dataframe
