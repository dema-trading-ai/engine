# Libraries
import abc

from pandas import DataFrame
import pandas as pd
from utils.utils import parse_timeframe
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
    timeframe: str

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

    def join_additional_data(self, dataframe, additional, timeframe, timeframe_additional, ffill=True):
        """
        This function is responsible for joining the additional data to the original dataframe
        """
        add_df = additional.copy()
        pair = add_df['pair'].unique()[0]

        timeframe_minutes = parse_timeframe(timeframe)
        timeframe_minutes_additional = parse_timeframe(timeframe_additional)

        if timeframe_minutes == timeframe_minutes_additional:
            add_df['date_merge'] = add_df["time"]
        elif timeframe_minutes < timeframe_minutes_additional:
            add_df['date_merge'] = (
                    add_df["time"] + pd.to_timedelta(timeframe_minutes_additional, 'ms').seconds * 1000 - pd.to_timedelta(timeframe_minutes, 'ms').seconds * 1000
            )
        else:
            raise ValueError("[Additional Data] Cannot join faster timeframe to slower timeframe")

        add_df.columns = [f"{col}_{pair}_{timeframe_additional}" for col in add_df.columns]

        dataframe = pd.merge(dataframe, add_df, left_on='time',
                             right_on=f'date_merge_{pair}_{timeframe_additional}', how='left')
        dataframe = dataframe.drop(f'date_merge_{pair}_{timeframe_additional}', axis=1)

        if ffill:
            dataframe = dataframe.ffill()

        return dataframe
