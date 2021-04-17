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

    def configure_stoploss(self, ohlcv: dict, data_dict: dict, strategy: Strategy) -> None:
        """
        Configures stoploss based on configured type.

        :param data_dict: dict containing OHLCV data of current pair
        :type data_dict: dict
        :param strategy: strategy class
        :type strategy: Strategy
        :return: None
        :rtype: None
        """
        if self.sl_type == 'standard':
            sl_price = self.open - (self.open * (abs(self.sl_perc) / 100))
        else:
            time = ohlcv['time']
            if self.sl_type == 'trailing':
                sl_sell_time, sl_price = self.trailing_stoploss(data_dict, time)
            elif self.sl_type == 'dynamic':
                sl_sell_time, sl_price = self.dynamic_stoploss(data_dict, time)
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

    def trailing_stoploss(self, data_dict: dict, time: int) -> [int, float]:
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

        :param data_dict: dict containing OHLCV data of current pair
        :type data_dict: dict
        :param time: time of current tick
        :type time: int
        :return: timestamp and price of first stoploss signal
        :rtype: list
        """
        # Calculates correct TSL% and adds TSL value for each tick
        stoploss_perc = 1 - (abs(self.sl_perc) / 100)
        trail = data_dict[str(time)]['close'] * stoploss_perc

        for timestamp in data_dict.keys():
            if int(timestamp) > time:
                ohlcv = data_dict[timestamp]
                stoploss = ohlcv['open'] * stoploss_perc
                if stoploss > trail:
                    trail = stoploss
                if ohlcv['low'] <= trail:
                    return ohlcv['time'], trail
        return np.NaN, np.NaN

    def dynamic_stoploss(self, data_dict: dict, time: int) -> [int, float]:
        """
        Finds the first occurence where the dynamic stoploss (defined in strategy)
        is triggered.

        :param data_dict: dict containing OHLCV data of current pair
        :type data_dict: dict
        :param time: time of current tick
        :type time: int
        :return: timestamp and price of first stoploss signal
        :rtype: list
        """
        for timestamp in data_dict.keys():
            if int(timestamp) > time:
                ohlcv = data_dict[timestamp]
                if ohlcv['stoploss'] == 1:
                    return ohlcv['time'], ohlcv['low']
        return np.NaN, np.NaN
