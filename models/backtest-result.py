from dataclasses import dataclass
from typing import Any

# ======================================================================
# BacktestResult is used for passing data from/to backtesting module
#
# © 2021 DemaTrading.AI
# ======================================================================

@dataclass
class BacktestResult:
    best_pair: Any = None
    max_drawdown: Any = None
    profit_percentage: Any = None
    profit_currency: Any = None
    pair_stats: Any = {}
    amount_of_trades: Any = None
    avg_duration: Any = None
    avg_duration_winners: Any = None
    avg_duraction_losers: Any = None