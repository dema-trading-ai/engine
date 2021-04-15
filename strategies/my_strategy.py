# Mandatory Imports
from pandas import DataFrame, Series
from backtesting.strategy import Strategy
from models.trade import Trade
from utils import plot_dataframe

# Optional Imports
import talib.abstract as ta


class MyStrategy(Strategy):
    """
    This is an example custom strategy, that inherits from the main Strategy class
    """

    min_candles = 21

    def generate_indicators(self, pair: str, dataframe: DataFrame) -> DataFrame:
        """
        :param dataframe: All passed candles (current candle included!) with OHLCV data
        :type dataframe: DataFrame
        :param pair: Certain coin pair in "AAA/BBB" format
        :type pair: string
        :return: Dataframe filled with indicator-data
        :rtype: DataFrame
        """
        # RSI - Relative Strength Index
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # EMA - Exponential Moving Average
        dataframe['ema5'] = ta.EMA(dataframe, timeperiod=5)
        dataframe['ema21'] = ta.EMA(dataframe, timeperiod=21)

        indicator_plot = 'ema5'
        plot_dataframe(pair, dataframe, indicator_plot)

        return dataframe

    def buy_signal(self, dataframe: DataFrame) -> DataFrame:
        """
        :param dataframe: Dataframe filled with indicators from generate_indicators
        :type indicators: DataFrame
        :return: dataframe filled with buy signals
        :rtype: DataFrame
        """
        if len(dataframe) > self.min_candles:
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
        :type indicators: DataFrame
        :return: dataframe filled with sell signals
        :rtype: DataFrame
        """
        if len(dataframe) > self.min_candles:
            # BEGIN STRATEGY

            dataframe.loc[
                (
                    (dataframe['rsi'] > 70) &
                    (dataframe['volume'] > 0)
                ),
                'sell'] = 1

            # END STRATEGY

        return dataframe
