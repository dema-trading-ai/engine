# Libraries
from datetime import datetime

# Files
from typing import Optional

from data.tradingmodule_config import TradingModuleConfig
from models.trade import Trade


# ======================================================================
# TradingModule is responsible for tracking trades, calling strategy methods
# and virtually opening / closing trades based on strategies' signal.
#
# © 2021 DemaTrading.ai
# ======================================================================


class TradingModule:
    max_open_trades = None
    closed_trades = []
    open_trades = []

    open_order_value_per_timestamp = {}
    budget_per_timestamp = {}
    realised_profits = []
    total_fee_amount = 0

    def __init__(self, config: TradingModuleConfig):
        print("[INFO] Initializing trading-module...")
        self.config = config
        self.budget = float(self.config.starting_capital)
        self.realised_profit = self.budget

        self.max_open_trades = int(self.config.max_open_trades)
        self.amount_of_pairs = len(self.config.pairs)
        self.fee = config.fee / 100
        self.sl_type = config.stoploss_type
        self.sl_perc = float(config.stoploss)

    def tick(self, ohlcv: dict, data_dict: dict) -> None:
        trade = self.find_open_trade(ohlcv['pair'])
        if trade:
            trade.update_stats(ohlcv)
            self.open_trade_tick(ohlcv, trade)
        else:
            self.no_trade_tick(ohlcv, data_dict)
        self.update_budget_per_timestamp_tracking(ohlcv)

    def no_trade_tick(self, ohlcv: dict, data_dict: dict) -> None:
        """
        Method is called when specified pair has no open trades
        :param ohlcv: dictionary with OHLCV data for current tick
        :type ohlcv: dict
        :param data_dict: dict containing OHLCV data of current pair
        :type data_dict: dict
        :return: None
        :rtype: None
        """
        if ohlcv['buy'] == 1:
            self.open_trade(ohlcv, data_dict)

    def open_trade_tick(self, ohlcv: dict, trade: Trade) -> None:
        """
        Method is called when specified pair has open trades.
        checks for ROI
        checks for stoploss
        :param ohlcv: dictionary with OHLCV data for current tick
        :type ohlcv: dict
        :param trade: Trade corresponding to tick pair
        :type trade: Trade
        :return: None
        :rtype: None
        """
        stoploss_reached = self.check_stoploss_open_trade(trade, ohlcv)
        roi_reached = self.check_roi_open_trade(trade, ohlcv)

        if stoploss_reached or roi_reached:
            return  # trade is closed by stoploss or ROI
        elif ohlcv['sell'] == 1:
            self.close_trade(trade, reason="Sell signal", ohlcv=ohlcv)
        else:  # trade is not closed
            self.update_value_per_timestamp_tracking(trade, ohlcv)

    def close_trade(self, trade: Trade, reason: str, ohlcv: dict) -> None:
        """
        :param trade: Trade model, trade to close
        :type trade: Trade
        :param reason: Reason for the trade to be closed (SL, ROI, Sell Signal)
        :type reason: string
        :param ohlcv: dictionary with OHLCV data for current tick
        :type ohlcv: dict
        :return: None
        :rtype: None
        """
        date = datetime.fromtimestamp(ohlcv['time'] / 1000)
        trade.close_trade(reason, date)

        self.total_fee_amount += trade.close_fee_amount
        self.budget += trade.capital

        self.open_trades.remove(trade)
        self.closed_trades.append(trade)
        self.update_realised_profit(trade)

    def open_trade(self, ohlcv: dict, data_dict: dict) -> None:
        """
        Method opens a trade for pair in ohlcv
        :param ohlcv: dictionary with OHLCV data for current tick
        :type ohlcv: dict
        :param data_dict: dict containing OHLCV data of current pair
        :type data_dict: dict
        :return: None
        :rtype: None
        """
        if self.budget <= 0:
            print("[INFO] Budget is running low, cannot buy")
            return

        # Find available trade spaces
        open_trades = len(self.open_trades)
        available_spaces = self.max_open_trades - open_trades
        if available_spaces == 0:
            return

        # Define spend amount based on realised profit
        spend_amount = (1. / self.amount_of_pairs) * self.realised_profit
        if spend_amount > self.budget:
            spend_amount = self.budget

        # Create new trade class
        date = datetime.fromtimestamp(ohlcv['time'] / 1000)
        new_trade = \
            Trade(ohlcv, spend_amount, self.fee, date, self.sl_type, self.sl_perc)
        new_trade.configure_stoploss(ohlcv, data_dict)
        new_trade.update_stats(ohlcv)

        # Update total budget with configured spend amount and fee
        self.total_fee_amount += spend_amount * self.fee
        self.budget -= spend_amount
        self.open_trades.append(new_trade)
        self.update_value_per_timestamp_tracking(new_trade, ohlcv)

    def check_roi_open_trade(self, trade: Trade, ohlcv: dict) -> bool:
        """
        :param trade: Trade model to check
        :type trade: Trade model
        :param ohlcv: dictionary with OHLCV data for current tick
        :type ohlcv: dict
        :return: return whether to close the trade based on ROI
        :rtype: boolean
        """
        time_passed = datetime.fromtimestamp(ohlcv['time'] / 1000) - trade.opened_at
        profit_percentage = (trade.profit_ratio - 1) * 100
        if profit_percentage > self.get_roi_over_time(time_passed):
            self.close_trade(trade, reason="ROI", ohlcv=ohlcv)
            return True
        return False

    def get_roi_over_time(self, time_passed: datetime) -> float:
        """
        Method that calculates the current ROI over time
        :param time_passed: Time passed since the trade opened
        :type time_passed: datetime in H:M:S
        :return: return the value of ROI
        :rtype: float
        """
        passed_minutes = time_passed.seconds / 60
        roi = self.config.roi['0']

        for key, value in sorted(self.config.roi.items(), key=lambda item: int(item[0])):
            if passed_minutes >= int(key):
                roi = value
        return roi

    def check_stoploss_open_trade(self, trade: Trade, ohlcv: dict) -> bool:
        """
        :param trade: Trade model to check
        :type trade: Trade model
        :param ohlcv: dictionary with OHLCV data for current tick
        :type ohlcv: dict
        :return: return whether the trade is closed or not
        :rtype: boolean
        """
        sl_signal = trade.check_for_sl(ohlcv)
        if sl_signal:
            self.close_trade(trade, reason="Stoploss", ohlcv=ohlcv)
            return True
        return False

    def find_open_trade(self, pair: str) -> Optional[Trade]:
        """
        :param pair: pair to check in "AAA/BBB" format
        :type pair: string
        :return: trade if found
        :rtype: Trade / None
        """
        for trade in self.open_trades:
            if trade.pair == pair:
                return trade
        return None

    def update_value_per_timestamp_tracking(self, trade: Trade, ohlcv: dict) -> None:
        """
        Method is used to be able to track the open trades value per timestamp
        :param trade: Any open trade
        :type trade: Trade
        :param ohlcv: dictionary with OHLCV data for current tick
        :type ohlcv: dict
        :return: None
        :rtype: None
        """
        try:
            self.open_order_value_per_timestamp[ohlcv['time']] += trade.capital
        except KeyError:
            self.open_order_value_per_timestamp[ohlcv['time']] = trade.capital

    def update_budget_per_timestamp_tracking(self, ohlcv: dict) -> None:
        """
        Used for tracking total budget per timestamp, used to be able to calculate
        max seen drawdown
        :param ohlcv: dictionary with OHLCV data for current tick
        :type ohlcv: dict
        :return: None
        :rtype: None
        """
        self.budget_per_timestamp[ohlcv['time']] = self.budget

    def update_realised_profit(self, trade: Trade) -> None:
        """
        This method updates realised profit after closing a trade
        :param trade: last closed Trade
        :type trade: Trade
        :return: None
        :rtype: None
        """
        self.realised_profit += trade.profit_dollar
        self.realised_profits.append(self.realised_profit)
