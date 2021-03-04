import numpy
import talib as ta

from models.trade import Trade
from pandas import DataFrame, Series

# ======================================================================
# Strategy-class is responsible for populating indicators / signals
#
# © 2021 DemaTrading.AI
# ======================================================================

"""This module defines the abstract base class (abc) that every strategie 
must inherit from, and override all methods"""


import abc

class Strategy(abc.ABC):
    min_candles = 21
    
    @abc.abstractmethod
    def generate_indicators(self, dataframe: DataFrame, current_candle: Series) -> DataFrame:
        pass 
    
    @abc.abstractmethod
    def buy_signal(self, dataframe: DataFrame, current_candle: Series) -> Series:
        pass

    @abc.abstractmethod
    def sell_signal(self, dataframe: DataFrame, current_candle: Series, trade: Trade) -> Series:
        pass
