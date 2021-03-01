from dataclasses import dataclass
from typing import Any

# ======================================================================
# PairStat class is used by backtesting module to format data for
# a nice table result (using Tabulate) in console.
#
# © 2021 DemaTrading.AI
# ======================================================================

@dataclass
class PairStat:
    pair_name: Any = None
    amount_of_trades: Any = None
    total_profit: Any = None
    avg_duration: Any = None