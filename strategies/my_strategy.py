from backtesting.strategy import Strategy
from pandas import DataFrame, Series
from models.trade import Trade

"""This is an example custom strategy, that inherits from 
the main Strategy class"""

class MyStrategy(Strategy):

    def generate_indicators(self, dataframe: DataFrame, current_candle: Series) -> DataFrame:
        return dataframe

    def buy_signal(self, dataframe: DataFrame, current_candle: Series) -> Series:
        current_candle['buy'] = 1
        return current_candle

    def sell_signal(self, dataframe: DataFrame, current_candle: Series, trade: Trade) -> Series:
        current_candle['sell'] = 0
        return current_candle
