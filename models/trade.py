# Libraries
from pandas import Series
from datetime import datetime


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
    stoploss = 0.0

    def __init__(self, ohlcv: Series, trade_amount: float, date: datetime):
        self.status = 'open'
        self.pair = ohlcv['pair']
        self.open = ohlcv['close']
        self.current = ohlcv['close']
        self.currency_amount = (trade_amount / ohlcv['close'])
        self.opened_at = date

    def close_trade(self, reason: str, date: datetime):
        """
        Closes this trade and updates stats according to latest data.
        """
        self.status = 'closed'
        self.sell_reason = reason
        self.close = self.current
        self.closed_at = date

    def update_stats(self, ohlcv: Series):
        """
        Updates states according to latest data.
        """
        self.current = ohlcv['close']
        self.profit_percentage = ((ohlcv['close'] - self.open) / self.open) * 100
        self.profit_dollar = (self.currency_amount * self.current) - (self.currency_amount * self.open)
