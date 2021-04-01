import abc
from pandas import DataFrame, Series
from models.trade import Trade
from typing import Optional

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
    def generate_indicators(self, candle_data: DataFrame) -> DataFrame:
        """
        :param candle_data: All passed candles (current candle included!) with OHLCV data
        :type candle_data: DataFrame
        :return: Dataframe filled with indicator-data
        :rtype: DataFrame
        """
        return

    @abc.abstractmethod
    def buy_signal(self, indicators: DataFrame, current_candle: DataFrame) -> DataFrame:
        """
        :param indicators: Dataframe filled with indicators from generate_indicators
        :type indicators: DataFrame
        :param current_candle: Last candle filled with indicators from generate_indicators
        :type current_candle: Series
        :return: Current candle filled with buy signals
        :rtype: Series
        """
        return

    @abc.abstractmethod
    def sell_signal(self, indicators: DataFrame, current_candle: DataFrame, trade: Trade) -> DataFrame:
        """
        :param indicators: dataframe filled with indicators from generate_indicators
        :type indicators: Dataframe
        :param current_candle: last candle filled with indicators from generate_indicators
        :type current_candle: Series
        :param trade: current open trade
        :type trade: Trade model
        :return: current candle filled with buy signals
        :rtype: Series
        """
        return

    def stoploss(self, indicators: DataFrame, current_candle: DataFrame, trade: Trade) -> Optional[float]:
        """
        Override this method if you want to dynamically change the stoploss 
        for every trade. If not, the stoploss provided in config.json will
        be returned.

        :param indicators: dataframe filled with indicators from generate_indicators
        :type indicators: Dataframe
        :param current_candle: last candle filled with indicators from generate_indicators
        :type current_candle: Series
        :param trade: current open trade
        :type trade: Trade model
        :return: the stoploss
        :rtype: float
        """
        return None

    @staticmethod
    def change_timeframe(candle_data: DataFrame, new_timeframe: str) -> DataFrame:
        """
        ### WORK IN PROGRESS ###

        Changes the timeframe of the given dataframe
        Remarks:
            - Returns only OHLC data (removes columns: 'time', 'volume', 'pair')
            - 'timeframe' in config.json needs to be smaller than new_timeframe to work correctly.
            - Values for new_timeframe can be found here:
            https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
        :param candle_data: All passed candles with OHLCV data
        :type candle_data: DataFrame
        :param timeframe: New timeframe configuration
        :type timeframe: string
        :return: Dataframe in new timeframe
        :rtype: DataFrame
        """
        return candle_data.resample(new_timeframe, origin='start', label='right').ohlc()
