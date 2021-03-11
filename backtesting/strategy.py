import talib as ta
import abc

from models.trade import Trade
from pandas import DataFrame, Series

# ======================================================================
# Strategy-class is responsible for populating indicators / signals
#
# © 2021 DemaTrading.AI
# ======================================================================
#
# This module defines the abstract base class (abc) that every strategie
# must inherit from, and override all methods


class Strategy(abc.ABC):
    min_candles = 21

    @abc.abstractmethod
    def generate_indicators(self, dataframe: DataFrame, current_candle: Series) -> DataFrame:
        """
        :param dataframe: All passed candles with OHLCV data
        :type dataframe: DataFrame
        :param current_candle: Last candle
        :type current_candle: Series
        :return: Dataframe filled with indicator-data
        :rtype: DataFrame
        """
        return dataframe
    
    @abc.abstractmethod
    def buy_signal(self, dataframe: DataFrame, current_candle: Series) -> Series:
        """
        :param dataframe: Dataframe filled with indicators created by generate_indicators method
        :type indicators: DataFrame
        :param current_candle: Last candle
        :type current_candle: Series
        :return: Dataframe filled with buy signals
        :rtype: DataFrame
        """
        pass

    @abc.abstractmethod
    def sell_signal(self, dataframe: DataFrame, current_candle: Series, trade: Trade) -> Series:
        """
        :param dataframe: Dataframe filled with indicators created by generate_indicators method
        :type indicators: DataFrame
        :param current_candle: Last candle
        :type current_candle: Series
        :param trade: Current open trade
        :type trade: Trade model
        :return: Dataframe filled with sell signals
        :rtype: DataFrame
        """
        pass

    @staticmethod
    def change_timeframe(dataframe: DataFrame, new_timeframe: str) -> DataFrame:
        """
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
