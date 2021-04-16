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
    sl_price = 0.0
    sl_sell_time = 0

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
        self.set_profits()

    def set_profits(self):
        """
        Sets profits corresponding to current info
        """
        self.profit_percentage = ((self.current - self.open) / self.open) * 100
        self.profit_dollar = (self.currency_amount * self.current) - (self.currency_amount * self.open)

    def configure_stoploss(self, ohlcv: dict, data_df: DataFrame, strategy: Strategy) -> None:
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
            sl_price = self.open - (self.open * (abs(self.sl_perc) / 100))
        else:
            time = str(ohlcv['time'])
            if self.sl_type == 'trailing':
                sl_sell_time, sl_price = self.trailing_stoploss(data_df, time)
            elif self.sl_type == 'dynamic':
                sl_sell_time, sl_price = self.dynamic_stoploss(data_df[time:])
            self.sl_sell_time = sl_sell_time
        self.sl_price = sl_price

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
        if self.sl_type == 'standard':
            if self.current < self.sl_price:
                self.current = self.sl_price
                self.set_profits()
                return True
        elif self.sl_type == 'trailing' or self.sl_type == 'dynamic':
            if self.sl_sell_time == ohlcv['time']:
                self.current = self.sl_price
                self.set_profits()
                return True
        return False

    def trailing_stoploss(self, data_df: DataFrame, time: str) -> [int, float]:
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
        :param time: time of current tick
        :type time: string
        :return: timestamp and price of first stoploss signal
        :rtype: list
        """

        def validate(value: float) -> float:
            """
            Extra function to determine the correct TSL value.
            """
            stoploss = value * self.stoploss_perc
            if stoploss > self.trail:
                self.trail = stoploss
            return self.trail

        # Calculates correct TSL% and adds TSL value for each tick
        self.stoploss_perc = 1 - (abs(self.sl_perc) / 100)
        self.trail = -np.inf
        data_df.loc[time:, 'trailing_value'] = data_df.loc[time:, 'open'].map(validate)

        # Finds first occurence where TSL is crossed
        np_time = np.array(data_df['time'])
        np_low = np.array(data_df['low'])
        np_trail = np.array(data_df['trailing_value'])
        index_list = np.argwhere(np_low <= np_trail)
        if index_list.any():  # stoploss is triggered somewhere
            index = index_list[0][0]
            return np_time[index], np_trail[index]
        return np.NaN, np.NaN

    def dynamic_stoploss(self, data_df: DataFrame) -> [int, float]:
        """
        Finds the first occurence where the dynamic stoploss (defined in strategy)
        is triggered.

        :param data_df: dataframe containing OHLCV data of current pair
        :type data_df: DataFrame
        :return: timestamp and price of first stoploss signal
        :rtype: list
        """
        np_time = np.array(data_df['time'])
        np_low = np.array(data_df['low'])
        np_stoploss = np.array(data_df['stoploss'])
        index_list = np.argwhere(np_stoploss == 1)
        if index_list.any():  # stoploss is triggered somewhere
            index = index_list[0][0]
            return np_time[index], np_low[index]
        return np.NaN, np.NaN


