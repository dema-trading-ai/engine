from backtesting.strategy import Strategy
from models.ohlcv import OHLCV
from models.trade import Trade
from datetime import datetime
import pandas as pd

# ======================================================================
# TradingModule is responsible for tracking trades, calling strategy methods
# and virtually opening / closing trades based on strategies' signal.
#
# © 2021 DemaTrading.AI
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

    def __init__(self, config):
        print("[INFO] Initializing trading-module")
        self.config = config
        self.strategy = Strategy()
        self.budget = float(self.config['starting-capital'])
        self.max_open_trades = int(self.config['max-open-trades'])

    def tick(self, ohlcv: pd.Series, data: pd.DataFrame) -> None:
        """
        :param ohlcv: OHLCV Model filled with tick-data
        :type ohlcv: OHLCV
        :param data: All passed ticks
        :type data: [OHLCV]
        :return: None
        :rtype: None
        """
        trade = self.find_open_trade(ohlcv['pair'])
        if trade:
            trade.update_stats(ohlcv)
            self.open_trade_tick(ohlcv, data, trade)
        else:
            self.no_trade_tick(ohlcv, data)
        self.update_budget_per_timestamp_tracking(ohlcv)

    def no_trade_tick(self, ohlcv: OHLCV, data: [OHLCV]):
        """
        Method is called when specified pair has no open trades
        populates buy signals
        :param ohlcv: OHLCV Model filled with tick-data
        :type ohlcv: OHLCV
        :return: None
        :rtype: None
        """
        indicators = self.strategy.generate_indicators(data, ohlcv)
        buy = self.strategy.buy_signal(indicators, ohlcv)
        if buy:
            self.open_trade(ohlcv)

    def open_trade_tick(self, ohlcv: OHLCV, data: [OHLCV], trade: Trade) -> None:
        """
        Method is called when specified pair has open trades.
        checks for ROI
        checks for SL
        populates Sell Signal
        :param ohlcv: OHLCV Model filled with tick-data
        :type ohlcv: OHLCV
        :param trade: Trade corresponding to tick pair
        :type Trade: Trade
        :return: None
        :rtype: None
        """
        self.update_value_per_timestamp_tracking(trade, ohlcv)  # update total value tracking

        # if current profit is below 0, update drawdown / check SL
        stoploss = self.check_stoploss_open_trade(trade, ohlcv)
        roi = self.check_roi_open_trade(trade, ohlcv)
        if stoploss or roi:
            return

        indicators = self.strategy.generate_indicators(data, ohlcv)
        sell = self.strategy.sell_signal(indicators, ohlcv, trade)

        if sell:
            self.close_trade(trade, reason="Sell signal", ohlcv=ohlcv)

    def close_trade(self, trade: Trade, reason: str, ohlcv: OHLCV) -> None:
        """
        :param trade: Trade model, trade to close
        :type trade: Trade
        :param reason: Reason for the trade to be closed (SL, ROI, Sell Signal)
        :type reason: string
        :param ohlcv: Last candle
        :type ohlcv: OHLCV model
        :return: None
        :rtype: None
        """
        date = datetime.fromtimestamp(ohlcv['time'] / 1000)
        trade.close_trade(reason, date)
        self.budget += trade.close * trade.currency_amount
        self.open_trades.remove(trade)
        self.closed_trades.append(trade)
        self.update_drawdowns_closed_trade(trade)

    def open_trade(self, ohlcv: OHLCV) -> None:
        """
        Method opens a trade for pair in ohlcv
        :param ohlcv: last OHLCV model (candle)
        :type ohlcv: OHLCV model
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
        new_trade = Trade(ohlcv, spend_amount, date)
        self.budget -= spend_amount
        self.open_trades.append(new_trade)
        self.update_value_per_timestamp_tracking(new_trade, ohlcv)

    def check_roi_open_trade(self, trade: Trade, ohlcv: OHLCV) -> bool:
        """
        :param trade: Trade model to check
        :type trade: Trade model
        :param ohlcv: last candle
        :type ohlcv: OHLCV model
        :return: return whether to close the trade based on ROI
        :rtype: boolean
        """
        if trade.profit_percentage > float(self.config['roi']):
            self.close_trade(trade, reason="ROI", ohlcv=ohlcv)
            return True
        return False

    def check_stoploss_open_trade(self, trade: Trade, ohlcv: OHLCV) -> bool:
        """
        :param trade: Trade model to check
        :type trade: Trade model
        :param ohlcv: last candle
        :type ohlcv: OHLCV model
        :return: return whether to close the trade based on Stop Loss
        :rtype: boolean
        """
        if trade.profit_percentage < 0:
            if trade.max_drawdown is None or trade.max_drawdown > trade.profit_percentage:
                trade.max_drawdown = trade.profit_percentage
            if trade.profit_percentage < float(self.config['stoploss']):
                self.close_trade(trade, reason="Stoploss", ohlcv=ohlcv)
                return True
        return False

    def find_open_trade(self, pair: str) -> Trade:
        """
        :param pair: pair to check in "AAA/BBB" format
        :type pair: string
        :return: trade if found
        :rtype: Trade model / None
        """
        for trade in self.open_trades:
            if trade.pair == pair:
                return trade
        return None

    def get_total_value_of_open_trades(self) -> float:
        """
        Method calculates the total value of all open trades

        :return: The total value in base-currency of all open trades
        :rtype: float
        """
        return_value = 0
        for trade in self.open_trades:
            return_value += (trade.currency_amount * trade.current)
        return return_value

    def update_value_per_timestamp_tracking(self, trade: Trade, ohlcv: OHLCV) -> None:
        """
        Method is used to be able to track the value change per timestamp per open trade
        next, this is used for calculating max seen drawdown
        :param trade: Any open trade
        :type trade: Trade model
        :param ohlcv: last candle
        :type ohlcv: OHLCV model
        :return: None
        :rtype: None
        """
        current_total_price = (trade.currency_amount * ohlcv['low'])
        try:
            self.open_order_value_per_timestamp[ohlcv['time']] += current_total_price
        except KeyError:
            self.open_order_value_per_timestamp[ohlcv['time']] = current_total_price

    def update_budget_per_timestamp_tracking(self, ohlcv: OHLCV) -> None:
        """
        Used for tracking total budget per timestamp, used to be able to calculate
        max seen drawdown

        :param ohlcv: last candle
        :type ohlcv: OHLCV Model
        :return: None
        :rtype: None
        """
        self.budget_per_timestamp[ohlcv['time']] = self.budget

    def update_drawdowns_closed_trade(self, trade: Trade) -> None:
        """
        This method updates realized drawdown tracking after closing a trade
        :param trade: last closed Trade
        :type trade: Trade Model
        :return: None
        :rtype: None
        """
        # this part is for setting the max_drawdown for 1 trade
        if trade.profit_percentage < self.max_drawdown:
            self.max_drawdown = trade.profit_percentage

        current_total_value = self.budget + self.get_total_value_of_open_trades()
        perc_of_total_value = ((trade.currency_amount * trade.close) / current_total_value) * 100
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
