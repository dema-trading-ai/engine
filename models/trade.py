# ======================================================================
# Trade class is used by TradingModule for registering trades and tracking
# stats while ticks pass.
#
# © 2021 DemaTrading.AI - Tijs Verbeek
# ======================================================================

class Trade:
    pair = None
    open = None
    current = None
    close = None
    status = None
    amount = None
    profit_dollar = None
    profit_percentage = None
    max_drawdown = None
    sell_reason = None
    opened_at = None
    closed_at = None
