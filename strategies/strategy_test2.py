from pandas import DataFrame, Series
from backtesting.strategy import Strategy
from models.trade import Trade
import talib.abstract as ta


class BullConfig(Strategy):
    # Variables
    min_candles = 200
    tradeMode = 0
    rsiThreshold = 49
    rsiMax = 79
    rsiBearThreshold = 70

    def generate_indicators(self, dataframe: DataFrame) -> DataFrame:
        # Indicators: RSI, ADX, MACD
        dataframe['rsiBull'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['rsiBear'] = ta.RSI(dataframe, timeperiod=7)
        dataframe['plusDI'] = ta.PLUS_DI(dataframe, timeperiod=20)
        dataframe['minusDI'] = ta.MINUS_DI(dataframe, timeperiod=20)

        macd = ta.MACD(dataframe, fastperiod=12, slowperiod=26, signalperiod=9)
        dataframe['macd'] = macd['macd']
        dataframe['macdsig'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']

        # EMA - Exponential Moving Average
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema200'] = ta.EMA(dataframe, timeperiod=200)

        return dataframe

    def buy_signal(self, dataframe: DataFrame, current_candle: DataFrame) -> DataFrame:

        if len(dataframe.index) > self.min_candles:
            # BEGIN STRATEGY

            index = len(dataframe.index) - 2
            prev_tick = dataframe.iloc[index]
            current_candle.loc[
                (
                        (current_candle['ema50'] > current_candle['ema200']) &
                        (current_candle['rsiBull'] > self.rsiThreshold) &
                        (current_candle['rsiBull'] < self.rsiMax) &
                        (current_candle['macd'] > current_candle['macdsig']) &
                        (prev_tick['macd'] < prev_tick['macdsig'])
                ),
                'buy'] = 1

            # END STRATEGY

        return current_candle

    def sell_signal(self, dataframe: DataFrame, current_candle: DataFrame, trade: Trade) -> DataFrame:

        if len(dataframe.index) > self.min_candles:
            # BEGIN STRATEGY

            index = len(dataframe.index) - 2
            prev_tick = dataframe.iloc[[index]]
            current_candle.loc[
                (
                        (current_candle['ema50'] > current_candle['ema200']) |
                        (
                                (current_candle['rsiBull'] < self.rsiThreshold) &
                                (current_candle['macd'] < current_candle['macdsig']) &
                                (prev_tick['macd'] > prev_tick['macdsig'])
                        )
                ),
                'sell'] = 1

            # END STRATEGY

        return current_candle
