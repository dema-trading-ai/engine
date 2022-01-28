# Libraries
from datetime import datetime, timedelta
from typing import Optional

# Files
from backtesting.strategy import Strategy
from cli.print_utils import print_info, print_warning
from modules.setup import ConfigModule
from modules.stats.trade import SellReason, Trade

# ======================================================================
# TradingModule is responsible for tracking trades, calling strategy methods
# and virtually opening / closing trades based on strategies' signal.
#
# © 2021 DemaTrading.ai
# ======================================================================


class TradingModule:

    def __init__(self, config: ConfigModule, strategy: Strategy):
        self.config = config
        self.strategy = strategy
        self.budget = float(self.config.starting_capital)
        self.realised_profit = self.budget

        self.max_open_trades = int(self.config.max_open_trades)
        self.exposure_per_trade = float(self.config.exposure_per_trade)
        self.amount_of_pairs = len(self.config.pairs)
        if self.amount_of_pairs < self.max_open_trades:
            print_warning("max_open_trades exceeds amount of pairs in whitelist. max_open_trades will be limited to "
                          "the amount of pairs in whitelist.")

        self.fee = config.fee / 100
        self.sl_type = config.stoploss_type
        self.sl_perc = float(config.stoploss)

        self.closed_trades = []
        self.open_trades = []
        self.budget_per_timestamp = {}
        self.capital_per_timestamp = {0: self.budget}
        self.realised_profits_per_timestamp = {0: self.budget}
        self.total_capital_open_trades = {}
        self.lowest_total_capital_open_trades = {}
        self.highest_total_capital_open_trades = {}
        self.total_fee_paid = 0
        self.rejected_buy_signal = 0
        self.buy_cooldown = {pair: 0 for pair in self.config.pairs}

    def tick(self, ohlcv: dict) -> None:
        trade = self.find_open_trade(ohlcv['pair'])
        if trade:
            trade.update_stats(ohlcv)
            self.open_trade_tick(ohlcv, trade)
        else:
            self.no_trade_tick(ohlcv)
        self.update_budget_per_timestamp(ohlcv)
        self.update_capital_per_timestamp(ohlcv)

    def no_trade_tick(self, ohlcv: dict, data_dict: dict) -> None:
        if self.buy_cooldown[ohlcv['pair']] > 0:
            self.buy_cooldown[ohlcv['pair']] -= 1
            return
        if ohlcv['buy'] == 1:
            self.open_trade(ohlcv)

    def open_trade_tick(self, ohlcv: dict, trade: Trade):
        stoploss_reached = self.check_stoploss_open_trade(trade, ohlcv)
        roi_reached = self.check_roi_open_trade(trade, ohlcv)

        if stoploss_reached and roi_reached:
            self.close_trade(trade, reason=SellReason.STOPLOSS_AND_ROI, ohlcv=ohlcv)
        elif stoploss_reached:
            self.close_trade(trade, reason=SellReason.STOPLOSS, ohlcv=ohlcv)
        elif roi_reached:
            self.close_trade(trade, reason=SellReason.ROI, ohlcv=ohlcv)
        elif ohlcv['sell'] == 1:
            self.close_trade(trade, reason=SellReason.SELL_SIGNAL, ohlcv=ohlcv)
        else:
            self.update_open_trades_value_per_timestamp(trade, ohlcv)

    def close_trade(self, trade: Trade, reason: SellReason, ohlcv: dict) -> None:

        date = datetime.fromtimestamp(ohlcv['time'] / 1000)
        trade.close_trade(reason, date)

        if trade.sell_reason == SellReason.STOPLOSS_AND_ROI:
            # Because trade had no impact on results, remove first issued fee from
            # total amount of fee and reset trade stats.
            self.total_fee_paid -= trade.fee_paid_open

            # Reset trade stats
            trade.capital = trade.starting_amount
            trade.update_profits(update_capital=False)
            trade.max_seen_drawdown = 1.0
        else:
            self.total_fee_paid += trade.fee_paid_close
        self.budget += trade.capital

        self.open_trades.remove(trade)
        self.closed_trades.append(trade)
        self.update_realised_profit(trade)

    def open_trade(self, ohlcv: dict, data_dict: dict) -> None:
        self.buy_cooldown[ohlcv['pair']] = self.strategy.buy_cooldown(trade)

        # Find available trade spaces
        open_trades = len(self.open_trades)
        available_spaces = self.max_open_trades - open_trades
        if available_spaces == 0:
            self.rejected_buy_signal += 1
            return

        if self.budget <= 0:
            self.rejected_buy_signal += 1
            print_info("Budget is running low, cannot buy")
            return

        # Define spend amount based on realised profit
        spend_amount = (
                               (1. / min(self.max_open_trades, self.amount_of_pairs)) * self.exposure_per_trade
                       ) * self.realised_profit
        if spend_amount > self.budget:
            spend_amount = self.budget

        # Create new trade class
        date = datetime.fromtimestamp(ohlcv['time'] / 1000)
        new_trade = \
            Trade(ohlcv, spend_amount, self.fee, date, self.sl_type, self.sl_perc)
        new_trade.configure_stoploss()
        new_trade.update_stats(ohlcv, first=True)

        # Update total budget with configured spend amount and fee
        self.total_fee_paid += spend_amount * self.fee
        self.budget -= spend_amount
        self.open_trades.append(new_trade)
        self.update_open_trades_value_per_timestamp(new_trade, ohlcv)

    def check_roi_open_trade(self, trade: Trade, ohlcv: dict) -> bool:
        time_passed = datetime.fromtimestamp(ohlcv['time'] / 1000) - trade.opened_at
        profit_percentage = ((ohlcv['high'] / trade.open) - 1.) * 100
        roi_percentage = self.get_roi_over_time(time_passed)

        if profit_percentage > roi_percentage:
            trade.current = trade.open * (1 + (roi_percentage / 100))
            trade.update_profits()
            return True
        return False

    def get_roi_over_time(self, time_passed: timedelta) -> float:
        passed_minutes = time_passed.seconds / 60
        roi = self.config.roi['0']

        for key, value in sorted(self.config.roi.items(), key=lambda item: int(item[0])):
            if passed_minutes >= int(key):
                roi = value
        return roi

    @staticmethod
    def check_stoploss_open_trade(trade: Trade, ohlcv: dict) -> bool:
        sl_signal = trade.check_for_sl(ohlcv)
        if sl_signal:
            return True
        return False

    def find_open_trade(self, pair: str) -> Optional[Trade]:
        for trade in self.open_trades:
            if trade.pair == pair:
                return trade
        return None

    def update_open_trades_value_per_timestamp(self, trade: Trade, ohlcv: dict) -> None:
        """
        Method is used to be able to track the open trades capitals per timestamp.
        It tracks the max seen point and the lowest seen point over all open trades.
        """
        trade_opened_at = trade.opened_at.timestamp() * 1000
        if trade_opened_at == ohlcv['time']:
            self.lowest_total_capital_open_trades[ohlcv['time']] = \
                self.lowest_total_capital_open_trades.get(ohlcv['time'], 0) + trade.starting_amount
            self.highest_total_capital_open_trades[ohlcv['time']] = \
                self.highest_total_capital_open_trades.get(ohlcv['time'], 0) + trade.starting_amount

        else:
            # When trade.candle_low is equal to trade.current in final candle, trade.capital could 
            # be lower than curr_low_capital due to fee.
            lowest_seen_capital = trade.candle_low * trade.currency_amount
            lowest_seen_capital = lowest_seen_capital if lowest_seen_capital < trade.capital \
                else trade.capital
            self.lowest_total_capital_open_trades[ohlcv['time']] = \
                self.lowest_total_capital_open_trades.get(ohlcv['time'], 0) + lowest_seen_capital

            # Update highest seen capital dict
            high_seen_capital = trade.candle_open * trade.currency_amount
            self.highest_total_capital_open_trades[ohlcv['time']] = \
                self.highest_total_capital_open_trades.get(ohlcv['time'], 0) + high_seen_capital

        # Update seen capital dict, on candle close value
        self.total_capital_open_trades[ohlcv['time']] = \
            self.total_capital_open_trades.get(ohlcv['time'], 0) + trade.capital

    def update_budget_per_timestamp(self, ohlcv: dict) -> None:
        self.budget_per_timestamp[ohlcv['time']] = self.budget

    def update_capital_per_timestamp(self, ohlcv: dict) -> None:
        self.capital_per_timestamp[ohlcv['time']] = \
            self.budget_per_timestamp[ohlcv['time']] + self.total_capital_open_trades.get(ohlcv['time'], 0)

    def update_realised_profit(self, trade: Trade) -> None:
        self.realised_profit += trade.profit_dollar
        self.realised_profits_per_timestamp[int(datetime.timestamp(trade.closed_at)*1000)] = self.realised_profit
