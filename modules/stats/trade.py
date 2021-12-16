# Libraries
import math
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
        self.close = None
        self.fee = fee
        self.open_fee_paid = spend_amount * fee
        self.close_fee_paid = None
        self.sell_reason = SellReason.NONE
        self.candle_low = None
        self.candle_open = None
        self.profit_ratio = None
        self.profit_dollar = None

        # Calculations for trade worth
        self.max_seen_drawdown = 1.0  # ratio
        self.starting_amount = spend_amount
        self.capital = spend_amount - self.open_fee_paid  # apply fee
        self.capital_per_timestamp = {}
        self.currency_amount = (self.capital / ohlcv['close'])

        # Stoploss configurations
        self.sl_type = sl_type
        self.sl_perc = sl_perc
        self.sl_static_price = None
        self.sl_sell_price = None
        self.sl_ratio = None
        self.update_profits()

    def close_trade(self, reason: SellReason, date: datetime) -> None:
        self.status = 'closed'
        self.sell_reason = reason
        self.close = self.current
        self.closed_at = date
        self.close_fee_paid = self.capital * self.fee  # final issued fee

        self.capital -= self.close_fee_paid
        self.update_profits(update_capital=False)

    def update_stats(self, ohlcv: dict, first: bool = False) -> None:
        self.current = ohlcv['close']
        self.update_profits()
        if not first:
            self.candle_low = ohlcv['low']
            self.candle_open = ohlcv['open']
            self.high = ohlcv['high']

    def update_profits(self, update_capital: bool = True):
        if update_capital:  # always triggers except when a trade is closed
            self.capital = self.currency_amount * self.current
        self.profit_ratio = self.capital / self.starting_amount
        self.profit_dollar = self.capital - self.starting_amount

    def configure_stoploss(self, ohlcv: dict) -> None:
        if self.sl_type == 'standard':  # for backwards compatability - can be removed in the future
            self.sl_type = 'static'
        if self.sl_type == 'static':
            self.sl_static_price = self.starting_amount * (1 - (abs(self.sl_perc) / 100))
        if self.sl_type == 'trailing':
            self.sl_ratio = 1 - (abs(self.sl_perc) / 100)
        if self.sl_type == 'dynamic':
            self.sl_sell_price = ohlcv['stoploss']

    def check_for_sl(self, ohlcv: dict) -> bool:
        if self.sl_type == 'static':
            lowest_capital = self.currency_amount * ohlcv['low']
            if lowest_capital <= self.sl_static_price:
                self.capital = min(self.currency_amount * ohlcv['open'], self.sl_static_price)
                self.update_profits(False)
                return True
        elif self.sl_type == 'trailing':
            lowest_ratio = ohlcv['low'] / self.high
            if lowest_ratio <= self.sl_ratio:
                self.current = (self.sl_ratio * self.starting_amount) / self.currency_amount
                self.update_profits()
                return True
        elif self.sl_type == 'dynamic':
            if self.sl_sell_price == ohlcv['time']:
                self.current = (self.sl_ratio * self.starting_amount) / self.currency_amount
                self.update_profits()
                return True
        return False
