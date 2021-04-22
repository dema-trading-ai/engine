# Libraries
import abc
from pandas import DataFrame, Series
from typing import Optional

# ======================================================================
# Strategy-class is responsible for populating indicators / signals
#
# © 2021 DemaTrading.ai
# ======================================================================

"""
ATTENTION: 

DO NOT USE THIS FILE TO IMPLEMENT YOUR STRATEGY. INSTEAD, USE my_strategy.py IN THE "strategies" FOLDER!
"""

class Strategy(abc.ABC):
    """
    This module defines the abstract base class (abc) that every strategy must inherit from.
    Methods defined in strategies/*.py will overwrite these methods.
    """

    @abc.abstractmethod
    def generate_indicators(self, dataframe: DataFrame) -> DataFrame:
        """
        :param dataframe: All passed candles (current candle included!) with OHLCV data
        :type dataframe: DataFrame
        :return: Dataframe filled with indicator-data
        :rtype: DataFrame
        """
        return

    def buy_signal(self, dataframe: DataFrame) -> DataFrame:
        """
        :param dataframe: Dataframe filled with indicators from generate_indicators
        :type dataframe: DataFrame
        :return: dataframe filled with buy signals
        :rtype: DataFrame
        """
        return

    def sell_signal(self, dataframe: DataFrame) -> DataFrame:
        """
        :param dataframe: Dataframe filled with indicators from generate_indicators
        :type dataframe: DataFrame
        :return: dataframe filled with sell signals
        :rtype: DataFrame
        """
        return

    def stoploss(self, dataframe: DataFrame) -> DataFrame:
        """
        Override this method if you want to dynamically change the stoploss 
        for every trade. If not, the stoploss provided in config.json will
        be returned.

        IMPORTANT: this function is only called when in the config.json "stoploss-type" is:
            ->  "stoploss-type": "dynamic"

        :param dataframe: dataframe filled with indicators from generate_indicators
        :type dataframe: Dataframe
        :return: dataframe filled with dynamic stoploss signals
        :rtype: DataFrame
        """
        return
