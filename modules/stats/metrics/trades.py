from datetime import timedelta
from statistics import median
import numpy as np

from modules.stats.trade import Trade


def calculate_best_worst_trade(closed_trades: [Trade]):
    best_trade_ratio = -np.inf
    best_trade_pair = ""
    worst_trade_ratio = np.inf
    worst_trade_pair = ""

    if len(closed_trades) > 0:
        best_trade = max(closed_trades,
                         key=lambda trade: trade.profit_ratio, default=-np.inf)
        best_trade_ratio = best_trade.profit_ratio
        best_trade_pair = best_trade.pair

        worst_trade = min(closed_trades,
                          key=lambda trade: trade.profit_ratio, default=np.inf)
        worst_trade_ratio = worst_trade.profit_ratio
        worst_trade_pair = worst_trade.pair

    return best_trade_ratio, best_trade_pair, worst_trade_ratio, worst_trade_pair


def get_number_of_losing_trades(closed_trades: [Trade]) -> int:
    nr_losing_trades = sum(1 for trade in closed_trades if trade.profit_ratio <= 1)
    return nr_losing_trades


def get_number_of_consecutive_losing_trades(closed_trades: [Trade]):
    nr_consecutive_trades = 0
    temp_nr_consecutive_trades = 0
    for trade in closed_trades:
        if trade.profit_ratio <= 1:
            temp_nr_consecutive_trades += 1
        else:
            temp_nr_consecutive_trades = 0
        nr_consecutive_trades = max(temp_nr_consecutive_trades, nr_consecutive_trades)
    return nr_consecutive_trades


def calculate_trade_durations(closed_trades: [Trade]):
    if len(closed_trades) > 0:
        shortest_trade_duration = min(trade.closed_at - trade.opened_at for trade in closed_trades)
        longest_trade_duration = max(trade.closed_at - trade.opened_at for trade in closed_trades)
        total_trade_duration = sum((trade.closed_at - trade.opened_at for trade in closed_trades), timedelta())
        avg_trade_duration = total_trade_duration / len(closed_trades)
    else:
        avg_trade_duration = longest_trade_duration = shortest_trade_duration = timedelta(0)
    return avg_trade_duration, longest_trade_duration, shortest_trade_duration


def compute_median_trade_profit(closed_trades: [Trade]) -> float:
    all_trade_profit = [trade.profit_dollar for trade in closed_trades]

    if len(all_trade_profit) == 0:
        return 0.0

    else:
        median_trade_profit = median(all_trade_profit)
        return median_trade_profit
