import pprint
from datetime import timedelta
from statistics import median

from modules.stats.trade import Trade


def compute_trade_rankings(closed_trades: [Trade]) -> dict:

    pairs = {trade.pair for trade in closed_trades}  # Find all pairs that have closed trades

    # Sort trades by pairs
    sorted_trades = {pair: [trade for trade in closed_trades if trade.pair == pair] for pair in pairs}

    rankings = {
        'ratio': dict(best=None, worst=None, median=None),
        'currency': dict(best=None, worst=None, median=None)
    }

    rankings_per_pair = {pair: rankings for pair in pairs}

    if len(closed_trades) > 0:
        for pair, trades in sorted_trades.items():
            for ranking_type in rankings.keys():
                trade_lst = [trade.profit_ratio if ranking_type == 'ratio'
                             else trade.profit_currency for trade in trades]
                rankings_per_pair[pair][ranking_type]['best'] = max(trade_lst)
                rankings_per_pair[pair][ranking_type]['worst'] = min(trade_lst)
                rankings_per_pair[pair][ranking_type]['median'] = median(trade_lst)
                pprint.pprint(rankings_per_pair)
                print(pair)
                print('-----------------------------------------')

    pprint.pprint(rankings_per_pair)

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
        return 0.0

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
