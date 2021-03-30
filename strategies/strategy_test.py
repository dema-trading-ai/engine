from pandas import DataFrame, Series
from backtesting.strategy import Strategy
from models.trade import Trade
import talib.abstract as ta


class BearConfig(Strategy):
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
        macd, macdsignal, macdhist = ta.MACD(dataframe, fastperiod=12, slowperiod=26, signalperiod=9)
        dataframe['macd'] = macd
        dataframe['macdsig'] = macdsignal
        dataframe['macdhist'] = macdhist
        # EMA - Exponential Moving Average
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema200'] = ta.EMA(dataframe, timeperiod=200)

        return dataframe

    def buy_signal(self, dataframe, current_candle):

        if len(dataframe.index) > self.min_candles and self.tradeMode == 0:
            # BEGIN STRATEGY

            index = len(dataframe.index) - 2
            prev_tick = dataframe.iloc[index]
            bth = self.rsiBearThreshold

            current_candle.loc[
                (
                        (current_candle['ema50'] < current_candle['ema200']) &
                        (current_candle['rsiBear'] > bth) &
                        (prev_tick['rsiBear'] < bth) &
                        (current_candle['plusDI'] > current_candle['minusDI'])
                ),
                'buy'] = 1

            found = current_candle['buy'].values

            if(found[0] == 1):
                print("======\nSHOULD BE BUYING\n======")

            # END STRATEGY

        return current_candle

    def sell_signal(self, dataframe, current_candle, trade):

        if len(dataframe.index) > self.min_candles:
            # BEGIN STRATEGY

            index = len(dataframe.index) - 2
            prev_tick = dataframe.iloc[[index]]
            current_candle.loc[
                (
                        (current_candle['rsiBear'] < self.rsiBearThreshold) &
                        (prev_tick['rsiBear'] > self.rsiBearThreshold)
                ),
                'sell'] = 1

        return dataframe
