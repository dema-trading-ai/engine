# Mandatory Imports
import talib.abstract as ta
from pandas import DataFrame
from backtesting.strategy import Strategy

# Optional Imports
from modules.setup.config import qtpylib_methods as qtpylib
from modules.stats.trade import Trade


class MyStrategy(Strategy):
    """
    This is an example custom strategy, that inherits from the main Strategy class
    """

    def generate_indicators(self, dataframe: DataFrame, additional_pairs=None) -> DataFrame:
        """
        :param dataframe: All passed candles (current candle included!) with OHLCV data
        :type dataframe: DataFrame
        :param additional_pairs: Possible additional pairs with specified timeframe
        :type additional_pairs: dict
        :return: Dataframe filled with indicator-data
        :rtype: DataFrame
        """
        # RSI - Relative Strength Index
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # EMA - Exponential Moving Average
        dataframe['ema5'] = ta.EMA(dataframe, timeperiod=5)
        dataframe['ema21'] = ta.EMA(dataframe, timeperiod=21)

        return dataframe

    def buy_signal(self, dataframe: DataFrame) -> DataFrame:
        """
        :param dataframe: Dataframe filled with indicators from generate_indicators
        :type dataframe: DataFrame
        :return: dataframe filled with buy signals
        :rtype: DataFrame
        """
        # BEGIN STRATEGY

        dataframe.loc[
            (
                (dataframe['rsi'] < 30) &
                (dataframe['ema5'] < dataframe['ema21']) &
                (dataframe['volume'] > 0)
            ),
            'buy'] = 1

        # END STRATEGY

        return dataframe

    def sell_signal(self, dataframe: DataFrame) -> DataFrame:
        """
        :param dataframe: Dataframe filled with indicators from generate_indicators
        :type dataframe: DataFrame
        :return: dataframe filled with sell signals
        :rtype: DataFrame
        """
        # BEGIN STRATEGY

        dataframe.loc[
            (
                (dataframe['rsi'] > 70) &
                (dataframe['volume'] > 0)
            ),
            'sell'] = 1

        # END STRATEGY

        return dataframe

    def buy_cooldown(self, last_trade: Trade) -> int:
        """
        Override this method if you want to add a buy cooldown when a trade is closed. This means that
        for the pair of the closed trade, a new trade cannot be opened for x time-steps.

        :param last_trade: The last trade that was closed
        :type last_trade: Trade
        :return: the amount of time-steps in which a new trade for the current pair may not be opened
        :rtype: int
        """
        return 5
