# Libraries
import abc

# from optuna import Trial
from pandas import DataFrame
import pandas as pd

from modules.public.trading_stats import TradingStats
# ======================================================================
# Strategy-class is responsible for populating indicators / signals
#
# © 2021 DemaTrading.ai
# ======================================================================
from utils.utils import parse_timeframe

"""
ATTENTION: 

DO NOT USE THIS FILE TO IMPLEMENT YOUR STRATEGY. INSTEAD, USE my_strategy.py IN THE "strategies" FOLDER!
"""


class Strategy(abc.ABC):
    """
    This module defines the abstract base class (abc) that every strategy must inherit from.
    Methods defined in strategies/*.py will overwrite these methods.
    """
    # trial: Trial = None
    timeframe: str

    @abc.abstractmethod
    def generate_indicators(self, dataframe: DataFrame) -> DataFrame:
        """
        :param dataframe: All passed candles (current candle included!) with OHLCV data
        :type dataframe: DataFrame
        :param additional_pairs: Possible additional pairs with specified timeframe
        :type additional_pairs: dict
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

    def join_additional_data(self, dataframe, additional_pair, original_timeframe, timeframe_additional, ffill=True):
        """
        This function is responsible for joining the additional data to the original dataframe. This is only possible
        if the additional timeframe is larger than the original timeframe. Furthermore some precautions have been taken
        such that candles are matched together without a looking in the future bias.
        :param dataframe: original Dataframe
        :param additional_pair: Dataframe of the additional pair
        :param original_timeframe: timeframe of original dataframe
        :param timeframe_additional: timeframe of additional dataframe
        :param ffill: Whether to forward fill the joined dataframe (recommended)
        """
        add_df = additional_pair.copy()
        pair = add_df['pair'].unique()[0]

        timeframe_ms = parse_timeframe(original_timeframe)
        timeframe_ms_additional = parse_timeframe(timeframe_additional)

        if timeframe_ms == timeframe_ms_additional:
            add_df['date_merge'] = add_df["time"]
        elif timeframe_ms < timeframe_ms_additional:
            add_df['date_merge'] = (
                    add_df["time"] + pd.to_timedelta(timeframe_ms_additional, 'ms').seconds * 1000 - pd.to_timedelta(timeframe_ms, 'ms').seconds * 1000
            )
        else:
            raise ValueError("[Additional Data] Cannot join faster timeframe to slower timeframe")

        add_df.columns = [f"{col}_{pair}_{timeframe_additional}" for col in add_df.columns]

        dataframe = pd.merge(dataframe, add_df, left_on='time',
                             right_on=f'date_merge_{pair}_{timeframe_additional}', how='left')
        dataframe = dataframe.drop(f'date_merge_{pair}_{timeframe_additional}', axis=1)

        if ffill:
            dataframe = dataframe.ffill()

        dataframe.set_index('time', drop=False, inplace=True)

        return dataframe

    def loss_function(self, stats: TradingStats) -> float:
        raise Exception("loss_function not implemented")
