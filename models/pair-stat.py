# ======================================================================
# PairStat class is used by backtesting module to format data for
# a nice table result (using Tabulate) in console.
#
# © 2021 DemaTrading.AI - Tijs Verbeek
# ======================================================================


class PairStat:
    pair_name = None
    amount_of_trades = None
    total_profit = None
    avg_duration = None