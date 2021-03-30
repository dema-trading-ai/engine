# Mandatory libraries
from pandas import DataFrame, Series
from backtesting.strategy import Strategy
from models.trade import Trade

# Optional libraries
import talib.abstract as ta


class DaanStrategy(Strategy):
    """
    This is an example custom strategy, that inherits from the main Strategy class
    """

    min_candles = 201

    def generate_indicators(self, dataframe: DataFrame) -> DataFrame:
        """
        :param dataframe: All passed candles (current candle included!) with OHLCV data
        :type dataframe: DataFrame
        :return: Dataframe filled with indicator-data
        :rtype: DataFrame
        """
        # RSI - Relative Strength Index
        dataframe['rsi'] = ta.RSI(dataframe)

        # EMA - Exponential Moving Average
        dataframe['sma200'] = ta.SMA(dataframe, timeperiod=200)
        dataframe['sma21'] = ta.SMA(dataframe, timeperiod=21)

        # bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=21, stds=2
        dataframe['sma20'] = ta.SMA(dataframe, timeperiod=20)
        dataframe['bb_upperband'] = dataframe['sma20'] + dataframe['sma20'].std() * 2
        dataframe['bb_lowerband'] = dataframe['sma20'] - dataframe['sma20'].std() * 2
        # dataframe['bb_lowerband'] = bollinger['lower']
        # dataframe['bb_middleband'] = bollinger['mid']
        # dataframe['bb_upperband'] = bollinger['upper']
        return dataframe

    def buy_signal(self, dataframe: DataFrame, current_candle: DataFrame) -> DataFrame:
        """
        :param dataframe: Dataframe filled with indicators from generate_indicators
        :type indicators: DataFrame
        :param current_candle: Last candle filled with indicators from generate_indicators
        :type current_candle: Series
        :return: Current candle filled with buy signals
        :rtype: Series
        """
        if len(dataframe.index) > self.min_candles:
            # BEGIN STRATEGY
            index = len(dataframe.index) - 2
            prev_tick = dataframe.iloc[index]
            # print(dataframe['close'])

            # print(dataframe['volume'].rolling(14).mean() * 2)
            current_candle.loc[
                (
                        (dataframe['volume'] > dataframe['volume'].rolling(14).mean() * 2) &
                        (dataframe['close'] < dataframe["sma21"]) &
                        # (dataframe['low'] < dataframe['bb_lowerband']) &
                        (dataframe['close'] < dataframe['sma200']) &
                        (prev_tick['rsi'] < 33) &
                        (dataframe['rsi'] > 33)
                        # (dataframe['close'] > dataframe['sma1d21'])
                ),
                'buy'] = 1

            # END STRATEGY

        return current_candle

    def sell_signal(self, dataframe: DataFrame, current_candle: DataFrame, trade: Trade) -> DataFrame:
        """
        :param dataframe: Dataframe filled with indicators from generate_indicators
        :type indicators: DataFrame
        :param current_candle: Last candle filled with indicators from generate_indicators
        :type current_candle: Series
        :param trade: Current open trade
        :type trade: Trade model
        :return: Current candle filled with buy signals
        :rtype: Series
        """
        if len(dataframe.index) > self.min_candles:
            # BEGIN STRATEGY

            current_candle.loc[
                (
                        (dataframe['rsi'] > 99.00) &
                        (current_candle['volume'] < 0)
                ),
                'sell'] = 1

            # END STRATEGY

        return current_candle
