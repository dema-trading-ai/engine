# ======================================================================
# BacktestResult is used for passing data from/to backtesting module
#
# © 2021 DemaTrading.AI
# ======================================================================


class BacktestResult:
    best_pair = None
    max_drawdown = None
    profit_percentage = None
    profit_currency = None
    pair_stats = {}
    amount_of_trades = None
    avg_duration = None
    avg_duration_winners = None
    avg_duraction_losers = None
