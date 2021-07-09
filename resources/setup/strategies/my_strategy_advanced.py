# Mandatory Imports
import talib.abstract as ta
from pandas import DataFrame
from backtesting.strategy import Strategy

# Optional Imports
import numpy as np


class MyStrategyAdvanced(Strategy):
    """
    This is an example custom strategy for advanced users, that inherits from the main Strategy class
    """

    def additional_pairs(self):
        """
        Specify The additional pairs in tuple format; ("pair", "timeframe")
        :return: list
        """
        return [
            ("BTC/USDT", "4h")
        ]

    def generate_indicators(self, dataframe: DataFrame, additional_pairs) -> DataFrame:
        """
        :param dataframe: All passed candles (current candle included!) with OHLCV data
        :type dataframe: DataFrame
        :return: Dataframe filled with indicator-data
        :rtype: DataFrame
        """
        # Select the BTC/USDT pair from the additional_pairs list
        add_btc_data = additional_pairs['BTC/USDT']
        # Add your indicators like usual
        add_btc_data['rsi'] = ta.RSI(add_btc_data, timeperiod=14)
        # Finally merge the additional btc data with the standard dataframe.
        # The new column will have the following format: ['<column>_<pair>_<timeframe>']
        dataframe = self.join_additional_data(dataframe, add_btc_data, self.timeframe, "4h")

        # RSI - Relative Strength Index
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # MFI - Money Flow Index
        dataframe['mfi'] = ta.MFI(dataframe)

        # EMA - Exponential Moving Average
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema200'] = ta.EMA(dataframe, timeperiod=200)

        # SMA - Simple Moving Average
        dataframe['sma'] = ta.SMA(dataframe, timeperiod=40)

        # MACD - Moving Average Convergence Divergence
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']

        # Minus Directional Indicator / Movement
        dataframe['minus_di'] = ta.MINUS_DI(dataframe)

        # Inverse Fisher transform on RSI, values [-1.0, 1.0]
        rsi = 0.1 * (dataframe['rsi'] - 50)
        dataframe['fisher_rsi'] = (np.exp(2 * rsi) - 1) / (np.exp(2 * rsi) + 1)

        # STOCHF - Stochastic Fast
        stoch_fast = ta.STOCHF(dataframe)
        dataframe['fastd'] = stoch_fast['fastd']
        dataframe['fastk'] = stoch_fast['fastk']

        # SAR (Stop And Reverse) Parabolic
        dataframe['sar'] = ta.SAR(dataframe)

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
                (
                    # BULL MARKET
                    (dataframe['ema50'] > dataframe['ema200']) &
                    (dataframe['fastd'] > dataframe['fastk']) &
                    (dataframe['volume'] > dataframe['volume'].rolling(200).mean() * 4) &
                    (dataframe['rsi'] > 50)
                )
                |
                (
                    # BEAR MARKET
                    (dataframe['ema50'] < dataframe['ema200']) &
                    (dataframe['rsi'] < 28) &
                    (dataframe['close'] < dataframe['sma']) &
                    (dataframe['fisher_rsi'] < -0.94) &
                    (dataframe['mfi'] < 16.0) &
                    (dataframe['fastd'] > dataframe['fastk']) &
                    (dataframe['fastd'] > 0)
                ) &
                (dataframe['rsi_BTC/USDT_4h'] < 30)     # additional pair usage
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
                (
                    # BULL MARKET
                    (dataframe['ema50'] > dataframe['ema200']) &
                    (dataframe['rsi'] > 60) &
                    (dataframe['macd'] < 0) &
                    (dataframe['minus_di'] > 0)
                )
                |
                (
                    # BEAR MARKET
                    (dataframe['ema50'] < dataframe['ema200']) &
                    (dataframe['sar'] > dataframe['close']) &
                    (dataframe['fisher_rsi'] > 0.3)
                )
            ),
            'sell'] = 1

        # END STRATEGY

        return dataframe

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
        # BEGIN STRATEGY

        dataframe['stoploss'] = dataframe['ema50']

        # END STRATEGY

        return dataframe
