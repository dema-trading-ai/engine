import abc
from pandas import DataFrame, Series
from models.trade import Trade

# ======================================================================
# Strategy-class is responsible for populating indicators / signals
#
# © 2021 DemaTrading.ai
# ======================================================================


class Strategy(abc.ABC):
    """
    This module defines the abstract base class (abc) that every strategy must inherit from.
    Methods defined in strategies/*.py will overwrite these methods.
    """

    min_candles = 21

    @abc.abstractmethod
    def generate_indicators(self, dataframe: DataFrame) -> DataFrame:
        """
        :param dataframe: All passed candles (current candle included!) with OHLCV data
        :type dataframe: DataFrame
        :return: Dataframe filled with indicator-data
        :rtype: DataFrame
        """
        return

    @abc.abstractmethod
    def buy_signal(self, dataframe: DataFrame, current_candle: DataFrame) -> DataFrame:
        """
        :param dataframe: Dataframe filled with indicators from generate_indicators
        :type indicators: DataFrame
        :param current_candle: Last candle filled with indicators from generate_indicators
        :type current_candle: Series
        :return: Current candle filled with buy signals
        :rtype: Series
        """
        return

    @abc.abstractmethod
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
        return

    @staticmethod
    def change_timeframe(dataframe: DataFrame, new_timeframe: str) -> DataFrame:
        """
        ### WORK IN PROGRESS ###

        Changes the timeframe of the given dataframe
        Remarks:
            - Returns only OHLC data (removes columns: 'time', 'volume', 'pair')
            - 'timeframe' in config.json needs to be smaller than new_timeframe to work correctly.
            - Values for new_timeframe can be found here:
            https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
        :param dataframe: All passed candles with OHLCV data
        :type indicators: DataFrame
        :param timeframe: New timeframe configuration
        :type timeframe: string
        :return: Dataframe in new timeframe
        :rtype: DataFrame
        """
        return dataframe.resample(new_timeframe, origin='start', label='right').ohlc()
