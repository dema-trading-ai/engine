import numpy
import talib as ta

from models.ohlcv import OHLCV
from models.trade import Trade
from pandas import DataFrame, Series

# ======================================================================
# Strategy-class is responsible for populating indicators / signals
#
# © 2021 DemaTrading.AI
# ======================================================================


class Strategy:
    min_candles = 21

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

    def buy_signal(self, dataframe: DataFrame, current_candle: Series) -> Series:
        """
        :param dataframe: Dataframe filled with indicators created by generate_indicators method
        :type indicators: DataFrame
        :param current_candle: Last candle
        :type current_candle: Series
        :return: Dataframe filled with buy signals
        :rtype: DataFrame
        """
        current_candle['buy'] = 1
        return current_candle

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
        current_candle['sell'] = 0
        return current_candle
