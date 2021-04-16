# Libraries
from pandas import DataFrame
from datetime import datetime
import numpy as np

# Files
from backtesting.strategy import Strategy


# ======================================================================
# Trade class is used by TradingModule for registering trades and tracking
# stats while ticks pass.
#
# © 2021 DemaTrading.AI
# ======================================================================


class Trade:
    pair = None
    open = 0.0
    current = 0.0
    close = 0.0
    status = None
    currency_amount = 0.0
    profit_dollar = 0.0
    profit_percentage = 0.0
    max_drawdown = 0.0
    sell_reason = None
    opened_at = 0.0
    closed_at = 0.0
    sl_dict = None
    sl_type = None
    sl_perc = 0.0
    trail = 0.0

    def __init__(self, ohlcv: dict, trade_amount: float, date: datetime, sl_type: str, sl_perc: float):
        self.status = 'open'
        self.pair = ohlcv['pair']
        self.open = ohlcv['close']
        self.current = ohlcv['close']
        self.currency_amount = (trade_amount / ohlcv['close'])
        self.opened_at = date
        self.sl_type = sl_type
        self.sl_perc = sl_perc

    def close_trade(self, reason: str, date: datetime) -> None:
        """
        Closes this trade and updates stats according to latest data.

        :param reason: reason why trade is closed
        :type reason: string
        :param date: date at which trade is opened
        :type date: datetime
        :return: None
        :rtype: None
        """
        self.status = 'closed'
        self.sell_reason = reason
        self.close = self.current
        self.closed_at = date

    def update_stats(self, ohlcv: dict) -> None:
        """
        Updates states according to latest data.

        :param ohlcv: dictionary with OHLCV data for current tick
        :type ohlcv: dict
        :return: None
        :rtype: None
        """
        self.current = ohlcv['close']
        self.profit_percentage = ((ohlcv['close'] - self.open) / self.open) * 100
        self.profit_dollar = (self.currency_amount * self.current) - (self.currency_amount * self.open)

    def configure_stoploss(self, data_df: DataFrame, strategy: Strategy) -> None:
        """
        Configures stoploss based on configured type.

        :param data_df: dataframe containing OHLCV data of current pair
        :type data_df: DataFrame
        :param strategy: strategy class
        :type strategy: Strategy
        :return: None
        :rtype: None
        """
        if self.sl_type == 'standard':
            self.sl_dict = self.standard_stoploss(data_df)
        elif self.sl_type == 'trailing':
            self.sl_dict = self.trailing_stoploss(data_df)
        elif self.sl_type == 'dynamic':
            dynamic_df = strategy.stoploss(data_df)
            self.sl_dict = dynamic_df.to_dict('index')

    def update_max_drawdown(self) -> None:
        """
        Updates max drawdown.

        :return: None
        :rtype: None
        """
        if self.profit_percentage < self.max_drawdown:
            self.max_drawdown = self.profit_percentage

    def check_for_sl(self, ohlcv: dict) -> bool:
        """
        Checks if the stoploss is crossed.

        :param ohlcv: dictionary with OHLCV data for current tick
        :type ohlcv: dict
        :return: boolean whether trade is clossed because of stoploss
        :rtype: boolean
        """
        timestamp = str(ohlcv['time'])
        candle = self.sl_dict[timestamp]
        if candle['stoploss'] == 1:
            if self.sl_type == 'standard':
                self.current = self.open - (self.open * (abs(self.sl_perc) / 100))
            elif self.sl_type == 'trailing':
                self.current = candle['trailing_value']
            elif self.sl_type == 'dynamic':
                self.current = candle['low']

            self.profit_percentage = ((self.current - self.open) / self.open) * 100
            self.profit_dollar = (self.currency_amount * self.current) - (self.currency_amount * self.open)
            return True
        return False

    def standard_stoploss(self, data_df: DataFrame) -> dict:
        """
        Calculated stoploss based on the opening price. If the price is x% under the
        trade opening price, the stoploss is triggered. 

        :param data_df: dataframe containing OHLCV data of current pair
        :type data_df: DataFrame
        :return: dict filled with stoploss signals
        :rtype: dict
        """
        stoploss_value = self.open - (self.open * (abs(self.sl_perc) / 100))
        data_df.loc[
            (
                (data_df['low'] < stoploss_value)
            ),
            'stoploss'] = 1

        return data_df.to_dict('index')

    def trailing_stoploss(self, data_df: DataFrame) -> dict:
        """
        Calculates the trailing stoploss (TSL) for each tick, applying the standard definition:
        - stoploss (SL) for a tick is calculated using: candle_open * (1 - trailing_percentage)
        - TSL algorithm:
            1. TSL is defined as the SL of first candle
            2. Get SL of next candle
            3. If SL for current candle is HIGHER than TSL:
                -> TSL = current candle SL
                -> back to Step 2.
            4. If SL for current candle is LOWER than TSL:
                -> back to Step 2.

        :param data_df: dataframe containing OHLCV data of current pair
        :type data_df: DataFrame
        :param trailing_perc: trailing percentage
        :type trailing_perc: float
        :return: dict filled with stoploss signals
        :rtype: dict
        """

        def validate(value: float) -> float:
            """
            Extra function to determine the correct TSL value.
            """
            if value > self.trail:
                self.trail = value
            return self.trail

        # Calculates correct TSL% and adds TSL value for each tick
        stoploss_perc = 1 - (abs(self.sl_perc) / 100)
        data_df['stoploss_value'] = data_df['open'] * stoploss_perc
        data_df['trailing_value'] = np.NaN

        # Gets first TSL value and finds trailing value at each timestamp
        self.trail = data_df['stoploss_value'].iloc[0]
        opened_at_ms = int(self.opened_at.timestamp() * 1000)   # datetime to ms
        data_df['trailing_value'] = data_df['stoploss_value'].map(lambda value: validate(value))

        # Checks if TSL is crossed
        data_df.loc[
            (
                (data_df['low'] <= data_df['trailing_value'])
            ),
            'stoploss'] = 1

        return data_df.to_dict('index')