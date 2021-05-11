# Libraries
from datetime import datetime
import numpy as np

# Files


# ======================================================================
# Trade class is used by TradingModule for registering trades and tracking
# stats while ticks pass.
#
# © 2021 DemaTrading.AI
# ======================================================================


class Trade:
    max_seen_drawdown: int = 0
    closed_at = None

    def __init__(self, ohlcv: dict, spend_amount: float, fee: float, date: datetime, sl_type: str, sl_perc: float):
        self.status = 'open'
        self.pair = ohlcv['pair']
        self.open = ohlcv['close']
        self.opened_at = date
        self.fee = fee
        self.starting_amount = spend_amount
        self.lowest_seen_price = spend_amount
        self.capital = spend_amount - (spend_amount * fee)  # apply fee
        self.currency_amount = (self.capital / ohlcv['close'])
        
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
        self.close_fee_amount = self.capital * self.fee   # final issued fee
        self.capital -= self.close_fee_amount
        self.set_profits(update_capital=False)

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
        self.update_max_drawdown()

    def set_profits(self, update_capital: bool = True):
        """
        Sets profits corresponding to current info
        """
        if update_capital:  # always triggers except when a trade is closed
            self.capital = self.currency_amount * self.current
        self.profit_ratio = self.capital / self.starting_amount
        self.profit_dollar = self.capital - self.starting_amount

    def configure_stoploss(self, ohlcv: dict, data_dict: dict) -> None:
        """
        Configures stoploss based on configured type.

        :param ohlcv: dictionary with OHLCV data for current tick
        :type ohlcv: dict
        :param data_dict: dict containing OHLCV data of current pair
        :type data_dict: dict
        :return: None
        :rtype: None
        """
        if self.sl_type == 'dynamic':
            if 'stoploss' in ohlcv:
                self.sl_sell_time, self.sl_price = self.dynamic_stoploss(data_dict, ohlcv['time'])
            else:
                self.sl_type = 'standard'   # when dynamic not configured use normal stoploss
        if self.sl_type == 'standard':
            self.sl_price = self.open - (self.open * (abs(self.sl_perc) / 100))
        elif self.sl_type == 'trailing':
            self.sl_sell_time, self.sl_price = self.trailing_stoploss(data_dict, ohlcv['time'])

    def update_max_drawdown(self) -> None:
        """
        Updates max drawdown.

        :return: None
        :rtype: None
        """
        if self.capital < self.lowest_seen_price:
            self.lowest_seen_price = self.capital
            self.max_seen_drawdown = self.profit_ratio

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
                return True
        elif self.sl_type == 'trailing' or self.sl_type == 'dynamic':
            if self.sl_sell_time == ohlcv['time']:
                self.current = self.sl_price
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
                if ohlcv['low'] < ohlcv['stoploss']:
                    return ohlcv['time'], ohlcv['stoploss']
        return np.NaN, np.NaN
