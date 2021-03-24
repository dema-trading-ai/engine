# Mandatory libraries
from pandas import DataFrame, Series
from backtesting.strategy import Strategy
from models.trade import Trade

# Optional libraries
import talib.abstract as ta


class MyStrategy(Strategy):
    """
    This is an example custom strategy, that inherits from the main Strategy class
    """

    min_candles = 21

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
        dataframe['ema5'] = ta.EMA(dataframe, timeperiod=5)
        dataframe['ema21'] = ta.EMA(dataframe, timeperiod=21)

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

            current_candle.loc[
                (
                    (current_candle['rsi'] < 30) &
                    (current_candle['ema5'] < current_candle['ema21']) &
                    (current_candle['volume'] > 0)
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
                    (current_candle['rsi'] > 70) &
                    (current_candle['volume'] > 0)
                ),
                'sell'] = 1

            # END STRATEGY

        return current_candle
