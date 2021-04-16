# Libraries
from pandas import DataFrame
from datetime import datetime

# Files
from config.load_strategy import load_strategy_from_config
from backtesting.strategy import Strategy
from models.trade import Trade
from utils import calculate_worth_of_open_trades



# ======================================================================
# TradingModule is responsible for tracking trades, calling strategy methods
# and virtually opening / closing trades based on strategies' signal.
#
# © 2021 DemaTrading.ai
# ======================================================================

class TradingModule:
    starting_budget = 0
    budget = 0
    max_open_trades = None

    config = None
    closed_trades = []
    open_trades = []
    max_drawdown = 0
    strategy = None

    open_order_value_per_timestamp = {}
    budget_per_timestamp = {}
    current_drawdown = 0.0
    realized_drawdown = 0

    fee = 0
    total_fee_amount = 0

    def __init__(self, config):
        print("[INFO] Initializing trading-module")
        self.config = config

        self.strategy = load_strategy_from_config(config)
        self.budget = float(self.config['starting-capital'])
        self.max_open_trades = int(self.config['max-open-trades'])
        self.fee = config['fee'] / 100
        self.sl_type = config['stoploss-type']
        self.sl_perc = float(config['stoploss'])

    def tick(self, ohlcv: dict, data_df: DataFrame) -> None:
        """
        :param ohlcv: dictionary with OHLCV data for current tick
        :type ohlcv: dict
        :param data_df: dataframe containing OHLCV data of current pair
        :type data_df: DataFrame
        :return: None
        :rtype: None
        """
        trade = self.find_open_trade(ohlcv['pair'])
        if trade:
            trade.update_stats(ohlcv)
            self.open_trade_tick(ohlcv, trade)
        else:
            self.no_trade_tick(ohlcv, data_df)
        self.update_budget_per_timestamp_tracking(ohlcv)

    def no_trade_tick(self, ohlcv: dict, data_df: DataFrame) -> None:
        """
        Method is called when specified pair has no open trades
        :param ohlcv: dictionary with OHLCV data for current tick
        :type ohlcv: dict
        :param data_df: dataframe containing OHLCV data of current pair
        :type data_df: DataFrame
        :return: None
        :rtype: None
        """
        if ohlcv['buy'] == 1:
            self.open_trade(ohlcv, data_df)

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
        self.update_value_per_timestamp_tracking(trade, ohlcv)  # update total value tracking
        trade.update_max_drawdown()

        stoploss_reached = self.check_stoploss_open_trade(trade, ohlcv)
        roi_reached = self.check_roi_open_trade(trade, ohlcv)

        if stoploss_reached or roi_reached:
            return  # trade is closed by stoploss or ROI
        elif ohlcv['sell'] == 1:
            self.close_trade(trade, reason="Sell signal", ohlcv=ohlcv)

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

        fee_amount = (trade.close * trade.currency_amount) * self.fee
        self.total_fee_amount += fee_amount

        self.budget += (trade.close * trade.currency_amount) - fee_amount
        self.open_trades.remove(trade)
        self.closed_trades.append(trade)
        self.update_drawdowns_closed_trade(trade)

    def open_trade(self, ohlcv: dict, data_df: DataFrame) -> None:
        """
        Method opens a trade for pair in ohlcv
        :param ohlcv: dictionary with OHLCV data for current tick
        :type ohlcv: dict
        :param data_df: dataframe containing OHLCV data of current pair
        :type data_df: DataFrame
        :return: None
        :rtype: None
        """
        if self.budget <= 0:
            print("[INFO] Budget is running low, cannot buy")
            return

        date = datetime.fromtimestamp(ohlcv['time'] / 1000)
        open_trades = len(self.open_trades)
        available_spaces = self.max_open_trades - open_trades
        spend_amount = (1. / available_spaces) * self.budget

        fee_amount = spend_amount * self.fee
        spend_amount -= fee_amount
        self.total_fee_amount += fee_amount
        
        new_trade = \
            Trade(ohlcv, spend_amount, date, self.sl_type, self.sl_perc)
        new_trade.configure_stoploss(ohlcv, data_df, self.strategy)

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
        if trade.profit_percentage > self.get_roi_over_time(time_passed):
            self.close_trade(trade, reason="ROI", ohlcv=ohlcv)
            return True
        return False

    def get_roi_over_time(self, time_passed) -> float:
        """
        Method that calculates the current ROI over time
        :param time_passed: Time passed since the trade opened
        :type time_passed: time in H:M:S
        :return: return the value of ROI
        :rtype: float
        """
        passed_minutes = time_passed.seconds / 60
        roi = self.config['roi']['0']

        for key, value in sorted(self.config['roi'].items(), key=lambda item: int(item[0])):
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

    def find_open_trade(self, pair: str) -> Trade:
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
        Method is used to be able to track the value change per timestamp per open trade
        next, this is used for calculating max seen drawdown
        :param trade: Any open trade
        :type trade: Trade
        :param ohlcv: dictionary with OHLCV data for current tick
        :type ohlcv: dict
        :return: None
        :rtype: None
        """
        current_total_price = (trade.currency_amount * ohlcv['low'])
        try:
            self.open_order_value_per_timestamp[ohlcv['time']] += \
                current_total_price
        except KeyError:
            self.open_order_value_per_timestamp[ohlcv['time']] = \
                current_total_price

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

    def update_drawdowns_closed_trade(self, trade: Trade) -> None:
        """
        This method updates realized drawdown tracking after closing a trade
        :param trade: last closed Trade
        :type trade: Trade
        :return: None
        :rtype: None
        """
        # this part is for setting the max_drawdown for 1 trade
        if trade.profit_percentage < self.max_drawdown:
            self.max_drawdown = trade.profit_percentage

        current_total_value = self.budget + \
            calculate_worth_of_open_trades(self.open_trades)
        perc_of_total_value = (
            (trade.currency_amount * trade.close) / current_total_value) * 100
        perc_influence = trade.profit_percentage * (perc_of_total_value / 100)

        # if the difference is drawdown, and no drawdown is realized at this moment, this is new drawdown.
        # else update the current drawdown with the profit percentage difference
        if perc_influence < 0 and self.current_drawdown >= 0:
            self.current_drawdown = perc_influence
        else:
            self.current_drawdown += perc_influence

        # if the current drawdown is bigger than the last realized drawdown, update it
        if self.current_drawdown < self.realized_drawdown:
            self.realized_drawdown = self.current_drawdown
