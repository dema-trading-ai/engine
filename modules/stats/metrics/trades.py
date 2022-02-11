from datetime import timedelta
from typing import Optional

from modules.stats.trade import Trade


def med(trades_return: [float, ...], default=None) -> Optional[float]:
    """Finds the median in a list of trade returns"""

    trades_return = sorted(trades_return)
    n = len(trades_return)
    if n == 0:
        return default
    if n % 2 == 1:
        return trades_return[n // 2]
    else:
        i = n // 2
        return (trades_return[i - 1] + trades_return[i]) / 2


def compute_trade_rankings(closed_trades: [Trade], pairs: list) -> dict:
    # Sort trades by pairs
    sorted_trades = {pair: [trade for trade in closed_trades if trade.pair == pair] for pair in pairs}

    rankings_per_pair = {pair: {
        'ratio': dict(best=None, worst=None, median=None),
        'currency': dict(best=None, worst=None, median=None)
    } for pair in pairs}

    if len(closed_trades) > 0:
        for pair, trades in sorted_trades.items():
            trades_profit_ratio = [trade.profit_ratio for trade in trades]
            trades_profit_currency = [trade.profit_currency for trade in trades]

            rankings_per_pair[pair]['ratio']['best'] = max(trades_profit_ratio, default=None)
            rankings_per_pair[pair]['ratio']['worst'] = min(trades_profit_ratio, default=None)
            rankings_per_pair[pair]['ratio']['median'] = med(trades_profit_ratio, default=None)
            rankings_per_pair[pair]['currency']['best'] = max(trades_profit_currency, default=None)
            rankings_per_pair[pair]['currency']['worst'] = min(trades_profit_currency, default=None)
            rankings_per_pair[pair]['currency']['median'] = med(trades_profit_currency, default=None)

    return rankings_per_pair


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


def compute_risk_reward_ratio(closed_trades: [Trade]) -> float:

    if len(closed_trades) == 0:
        return 0

    winning_trades = []
    losing_trades = []

    for trade in closed_trades:  # Ignore trades with a profit of 0

        if trade.profit_currency > 0:
            winning_trades.append(trade.profit_currency)
            continue

        if trade.profit_currency < 0:
            losing_trades.append(trade.profit_currency)

    total_gain = sum(winning_trades)
    total_loss = sum(losing_trades)

    count_winning_trades = len(winning_trades)
    count_losing_trades = len(losing_trades)

    if count_winning_trades == 0 or count_losing_trades == 0 or total_gain == 0 or total_loss == 0:
        return 0.0

    avg_gain = total_gain / count_winning_trades
    avg_loss = total_loss / count_losing_trades

    risk_reward_ratio = avg_gain / abs(avg_loss)

    return risk_reward_ratio
