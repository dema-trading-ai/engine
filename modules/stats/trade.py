# Libraries
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np


# Files


# ======================================================================
# Trade class is used by TradingModule for registering trades and tracking
# stats while ticks pass.
#
# © 2021 DemaTrading.AI
# ======================================================================


class SellReason(Enum):
    SELL_SIGNAL = "Sell Signal"
    STOPLOSS = "Stoploss"
    ROI = "ROI"
    STOPLOSS_AND_ROI = "Stoploss and ROI"
    NONE = "None"


class Trade:
    max_seen_drawdown: float
    closed_at: Any
    sell_reason: SellReason

    def __init__(self, ohlcv: dict, spend_amount: float, fee: float, date: datetime, sl_type: str, sl_perc: float):
        # Basic trade data
        self.status = 'open'
        self.pair = ohlcv['pair']
        self.open = ohlcv['close']
        self.current = ohlcv['close']
        self.opened_at = date
        self.closed_at = None
        self.fee = fee
        self.sell_reason = SellReason.NONE

        # Calculations for trade worth
        self.max_seen_drawdown = 1.0  # ratio
        self.starting_amount = spend_amount
        self.capital = spend_amount - (spend_amount * fee)  # apply fee
        self.currency_amount = (self.capital / ohlcv['close'])

        # Variables for max seen drawdown
        self.max_seen_drawdown = 1.0
        self.curr_seen_drawdown = 1.0
        self.curr_highest_seen_capital = spend_amount
        self.curr_lowest_seen_capital = spend_amount

        # Stoploss configurations
        self.sl_type = sl_type
        self.sl_perc = sl_perc
        self.update_profits()

    def close_trade(self, reason: SellReason, date: datetime) -> None:
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
        self.close_fee_paid = self.capital * self.fee   # final issued fee

        self.capital -= self.close_fee_paid
        self.update_profits(update_capital=False)

        # Check if last capital exceeds lowest seen capital (because of issued fee)
        if self.capital < self.curr_lowest_seen_capital:
            seen_drawdown = self.capital / self.curr_highest_seen_capital
            # Check if new seen drawdown exceeds max seen drawdown
            if seen_drawdown < self.max_seen_drawdown:
                self.max_seen_drawdown = seen_drawdown

    def update_stats(self, ohlcv: dict, first: bool = False) -> None:
        self.current = ohlcv['close']
        self.update_profits()
        if not first:
            self.candle_low = ohlcv['low']
            self.candle_open = ohlcv['open']
            self.update_max_drawdown()

    def update_profits(self, update_capital: bool = True):
        if update_capital:  # always triggers except when a trade is closed
            self.capital = self.currency_amount * self.current
        self.profit_ratio = self.capital / self.starting_amount
        self.profit_dollar = self.capital - self.starting_amount

    def configure_stoploss(self, ohlcv: dict, data_dict: dict) -> None:
        if self.sl_type == 'dynamic':
            if 'stoploss' in ohlcv:
                self.sl_sell_time, self.sl_ratio = self.dynamic_stoploss(data_dict, ohlcv['time'])
            else:
                self.sl_type = 'standard'   # when dynamic not configured use normal stoploss
        if self.sl_type == 'standard':
            self.sl_ratio = 1 - (abs(self.sl_perc) / 100)
        elif self.sl_type == 'trailing':
            self.sl_sell_time, self.sl_ratio = self.trailing_stoploss(data_dict, ohlcv['time'])

    def update_max_drawdown(self) -> None:
        """
        Updates max seen drawdown defined as: biggest difference between
        highest peak of candle 'open' and lowest bottom of candle 'low'.
        """
        temp_max_capital = self.candle_open * self.currency_amount
        temp_lowest_capital = self.candle_low * self.currency_amount
        
        # Check for new drawdown period
        if temp_max_capital > self.curr_highest_seen_capital:
            # Reset temp seen drawdown stats
            self.curr_highest_seen_capital = temp_max_capital
            self.curr_lowest_seen_capital = temp_max_capital
            self.curr_seen_drawdown = 1.0   # ratio w/ respect to peak

        # Check if drawdown reached new bottom
        if temp_lowest_capital < self.curr_lowest_seen_capital:
            self.curr_lowest_seen_capital = temp_lowest_capital
            self.curr_seen_drawdown = temp_lowest_capital / self.curr_highest_seen_capital

        # If temp drawdown is larger than max drawdown, update max drawdown
        if self.curr_seen_drawdown < self.max_seen_drawdown:
            self.max_seen_drawdown = self.curr_seen_drawdown

    def check_for_sl(self, ohlcv: dict) -> bool:
        if self.sl_type == 'standard':
            lowest_ratio = (ohlcv['low'] * self.currency_amount) / self.starting_amount
            if lowest_ratio <= self.sl_ratio:
                self.current = (self.sl_ratio * self.starting_amount) / self.currency_amount
                self.update_profits()
                return True
        elif self.sl_type == 'trailing' or self.sl_type == 'dynamic':
            if self.sl_sell_time == ohlcv['time']:
                self.current = (self.sl_ratio * self.starting_amount) / self.currency_amount
                self.update_profits()
                return True
        return False

    def trailing_stoploss(self, data_dict: dict, time: int) -> tuple:
        """
        Calculates the trailing stoploss (TSL) for each tick, applying the standard definition:
        - stoploss (SL) for a tick is calculated using: candle_high * (1 - trailing_percentage)
        - TSL algorithm:
            1. TSL is defined as the SL of first candle
            2. Get SL of next candle
            3. If SL for current candle is HIGHER than TSL:
                -> TSL = current candle SL
                -> back to Step 2.
            4. If SL for current candle is LOWER than TSL:
                -> back to Step 2.
        """
        # Calculates correct TSL% and adds TSL value for each tick
        stoploss_perc = (abs(self.sl_perc) / 100)
        trail_ratio = 1 - stoploss_perc
        for timestamp in data_dict.keys():
            if int(timestamp) > time:
                ohlcv = data_dict[timestamp]
                # Update trail ratio
                stoploss_ratio = (ohlcv['high'] * self.currency_amount) * (1-stoploss_perc) / self.starting_amount
                if stoploss_ratio > trail_ratio:
                    trail_ratio = stoploss_ratio

                # Check if lowest ratio crossed trail ratio
                lowest_ratio = ((ohlcv['low'] * self.currency_amount) * stoploss_perc) / self.starting_amount
                if lowest_ratio <= trail_ratio:
                    return ohlcv['time'], trail_ratio
        return np.NaN, np.NaN

    def dynamic_stoploss(self, data_dict: dict, time: int) -> tuple:
        """
        Finds the first occurrence where the dynamic stoploss (defined in strategy)
        is triggered.
        """
        for timestamp in data_dict.keys():
            if int(timestamp) > time:
                ohlcv = data_dict[timestamp]
                if ohlcv['low'] <= ohlcv['stoploss']:
                    low_value = min(ohlcv["stoploss"], ohlcv["open"])
                    sl_ratio = (low_value * self.currency_amount) / self.starting_amount
                    return ohlcv['time'], sl_ratio
        return np.NaN, np.NaN
