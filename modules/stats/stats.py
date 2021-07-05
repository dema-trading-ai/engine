from datetime import datetime, timedelta

from pandas import DataFrame
from tqdm import tqdm
import numpy as np

from modules.output.results import CoinInsights, MainResults, LeftOpenTradeResult
from modules.pairs_data import PairsData
from modules.stats.drawdown.drawdown import get_max_drawdown_ratio
from modules.stats.drawdown.per_coin import get_max_seen_drawdown_per_coin, get_max_realised_drawdown_per_coin
from modules.stats.drawdown.for_portfolio import get_max_seen_drawdown_for_portfolio, \
    get_max_realised_drawdown_for_portfolio
from modules.stats.drawdown.per_trade import get_max_seen_drawdown_per_trade
from modules.stats.stats_config import StatsConfig
from modules.stats.trade import Trade, SellReason
from modules.stats.trading_stats import TradingStats
from modules.stats.tradingmodule import TradingModule
from collections import defaultdict

from utils.dict import group_by
from utils.utils import calculate_worth_of_open_trades


def calculate_best_worst_trade(closed_trades):
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


def get_number_of_consecutive_losing_trades(closed_trades):
    nr_consecutive_trades = 0
    temp_nr_consecutive_trades = 0
    for trade in closed_trades:
        if trade.profit_ratio <= 1:
            temp_nr_consecutive_trades += 1
        else:
            temp_nr_consecutive_trades = 0
        nr_consecutive_trades = max(temp_nr_consecutive_trades, nr_consecutive_trades)
    return nr_consecutive_trades


def calculate_trade_durations(closed_trades):
    if len(closed_trades) > 0:
        shortest_trade_duration = min(trade.closed_at - trade.opened_at for trade in closed_trades)
        longest_trade_duration = max(trade.closed_at - trade.opened_at for trade in closed_trades)
        total_trade_duration = sum((trade.closed_at - trade.opened_at for trade in closed_trades), timedelta())
        avg_trade_duration = total_trade_duration / len(closed_trades)
    else:
        avg_trade_duration = longest_trade_duration = shortest_trade_duration = timedelta(0)
    return avg_trade_duration, longest_trade_duration, shortest_trade_duration


def get_market_drawdown(pairs: list, data_dict: dict) -> dict:
    market_drawdown = {}
    total_drawdown = [0] * len(data_dict[pairs[0]])
    for pair in pairs:
        values_list = [data_dict[pair][d].get('close') for d in data_dict[pair]]
        coin_values = DataFrame(values_list, columns=['value'])
        market_drawdown[pair] = get_max_drawdown_ratio(coin_values)
        values_list = [x / values_list[0] for x in values_list]
        total_drawdown = map(lambda x, y: x + y, total_drawdown, values_list)
    market_drawdown['all'] = get_max_drawdown_ratio(DataFrame(total_drawdown, columns=['value']))
    return market_drawdown


class StatsModule:
    buy_points = None
    sell_points = None

    def __init__(self, config: StatsConfig, frame_with_signals: PairsData, trading_module: TradingModule, df):
        self.df = df
        self.config = config
        self.trading_module = trading_module
        self.frame_with_signals = frame_with_signals

    def analyze(self) -> TradingStats:
        pairs = list(self.frame_with_signals.keys())
        ticks = list(self.frame_with_signals[pairs[0]].keys()) if pairs else []

        for tick in tqdm(ticks, desc='[INFO] Backtesting', total=len(ticks), ncols=75):
            for pair in pairs:
                pair_dict = self.frame_with_signals[pair]
                tick_dict = pair_dict[tick]
                self.trading_module.tick(tick_dict, pair_dict)

        market_change = get_market_change(ticks, pairs, self.frame_with_signals)
        market_drawdown = get_market_drawdown(pairs, self.frame_with_signals)
        return self.generate_backtesting_result(market_change, market_drawdown)

    def generate_backtesting_result(self, market_change: dict, market_drawdown: dict) -> TradingStats:

        trading_module = self.trading_module

        coin_results = self.generate_coin_results(trading_module.closed_trades, market_change, market_drawdown)
        best_trade_ratio, best_trade_pair, worst_trade_ratio, worst_trade_pair = \
            calculate_best_worst_trade(trading_module.closed_trades)
        open_trade_results = self.get_left_open_trades_results(trading_module.open_trades)

        main_results = self.generate_main_results(
            trading_module.open_trades,
            trading_module.closed_trades,
            trading_module.budget,
            market_change,
            market_drawdown,
            best_trade_ratio,
            best_trade_pair,
            worst_trade_ratio,
            worst_trade_pair)
        self.calculate_statistics_for_plots(trading_module.closed_trades, trading_module.open_trades)

        return TradingStats(
            main_results=main_results,
            coin_results=coin_results,
            open_trade_results=open_trade_results,
            frame_with_signals=self.frame_with_signals,
            buypoints=self.buy_points,
            sellpoints=self.sell_points,
            df=self.df,
            trades=trading_module.open_trades + trading_module.closed_trades
        )

    def generate_main_results(self, open_trades: [Trade], closed_trades: [Trade], budget: float,
                              market_change: dict, market_drawdown: dict, best_trade_ratio: float,
                              best_trade_pair: str, worst_trade_ratio: float,
                              worst_trade_pair: str) -> MainResults:
        # Get total budget and calculate overall profit
        budget += calculate_worth_of_open_trades(open_trades)
        overall_profit_percentage = ((budget - self.config.starting_capital) / self.config.starting_capital) * 100

        # Find max seen and realised drawdown
        max_realised_drawdown = get_max_realised_drawdown_for_portfolio(
            self.trading_module.realised_profits_per_timestamp
        )
        max_seen_drawdown = get_max_seen_drawdown_for_portfolio(
            self.trading_module.capital_per_timestamp
        )

        nr_losing_trades = get_number_of_losing_trades(closed_trades)
        nr_consecutive_losing_trades = get_number_of_consecutive_losing_trades(closed_trades)

        best_trade_profit_percentage = (best_trade_ratio - 1) * 100 \
            if best_trade_ratio != -np.inf else 0
        worst_trade_profit_percentage = (worst_trade_ratio - 1) * 100 \
            if worst_trade_ratio != np.inf else 0

        avg_trade_duration, longest_trade_duration, shortest_trade_duration = calculate_trade_durations(closed_trades)

        tested_from = datetime.fromtimestamp(self.config.backtesting_from / 1000)
        tested_to = datetime.fromtimestamp(self.config.backtesting_to / 1000)

        timespan_seconds = (tested_to - tested_from).total_seconds()
        nr_days = timespan_seconds / timedelta(days=1).total_seconds()

        return MainResults(tested_from=tested_from,
                           tested_to=tested_to,
                           max_open_trades=self.config.max_open_trades,
                           market_change_coins=(market_change['all'] - 1) * 100,
                           market_drawdown_coins=(market_drawdown['all'] - 1) * 100,
                           market_change_btc=(self.config.btc_marketchange_ratio - 1) * 100,
                           market_drawdown_btc=(self.config.btc_drawdown_ratio - 1) * 100,
                           starting_capital=self.config.starting_capital,
                           end_capital=budget,
                           overall_profit_percentage=overall_profit_percentage,
                           n_trades=len(open_trades) + len(closed_trades),
                           n_average_trades=(len(open_trades) + len(closed_trades)) / nr_days,
                           n_left_open_trades=len(open_trades),
                           n_trades_with_loss=nr_losing_trades,
                           n_consecutive_losses=nr_consecutive_losing_trades,
                           max_realised_drawdown=(max_realised_drawdown-1) * 100,
                           worst_trade_profit_percentage=worst_trade_profit_percentage,
                           worst_trade_pair=worst_trade_pair,
                           best_trade_profit_percentage=best_trade_profit_percentage,
                           best_trade_pair=best_trade_pair,
                           avg_trade_duration=avg_trade_duration,
                           longest_trade_duration=longest_trade_duration,
                           shortest_trade_duration=shortest_trade_duration,
                           max_seen_drawdown=(max_seen_drawdown['drawdown']-1) * 100,
                           drawdown_from=max_seen_drawdown['from'],
                           drawdown_to=max_seen_drawdown['to'],
                           drawdown_at=max_seen_drawdown['at'],
                           stoploss=self.config.stoploss,
                           stoploss_type=self.config.stoploss_type,
                           fee=self.config.fee,
                           total_fee_amount=self.trading_module.total_fee_paid)

    def generate_coin_results(self, closed_trades: [Trade], market_change: dict, market_drawdown: dict) -> [list, dict]:
        stats = self.calculate_statistics_per_coin(closed_trades)
        new_stats = []

        for coin in stats:
            avg_profit_prct = (stats[coin]['cum_profit_prct'] / stats[coin]['amount_of_trades']) \
                if stats[coin]['amount_of_trades'] > 0 else 0

            coin_insight = CoinInsights(pair=coin,
                                        n_trades=stats[coin]['amount_of_trades'],
                                        market_change=(market_change[coin] - 1) * 100,
                                        market_drawdown=(market_drawdown[coin] - 1) * 100,
                                        cum_profit_percentage=stats[coin]['cum_profit_prct'],
                                        total_profit_percentage=(stats[coin]['total_profit_ratio'] - 1) * 100,
                                        avg_profit_percentage=avg_profit_prct,
                                        profit=stats[coin]['total_profit_amount'],
                                        max_seen_drawdown=(stats[coin]['max_seen_ratio'] - 1) * 100,
                                        max_realised_drawdown=(stats[coin]['max_realised_ratio'] - 1) * 100,
                                        avg_trade_duration=stats[coin]['avg_trade_duration'],
                                        longest_trade_duration=stats[coin]['longest_trade_duration'],
                                        shortest_trade_duration=stats[coin]['shortest_trade_duration'],
                                        roi=stats[coin]['sell_reasons'][SellReason.ROI],
                                        stoploss=stats[coin]['sell_reasons'][SellReason.STOPLOSS],
                                        sell_signal=stats[coin]['sell_reasons'][SellReason.SELL_SIGNAL])
            new_stats.append(coin_insight)

        return new_stats

    def calculate_statistics_per_coin(self, closed_trades):
        per_coin_stats = {
            pair: {
                'cum_profit_prct': 0,
                'total_profit_ratio': 1.0,
                'total_profit_amount': 0.0,
                'amount_of_trades': 0,
                'peak_ratio': 1.0,
                'drawdown_ratio': 1.0,
                'total_ratio': 1.0,
                'max_seen_ratio': 1.0,
                'max_realised_ratio': 1.0,
                'total_duration': None,
                'sell_reasons': defaultdict(int),
                "avg_trade_duration": timedelta(0),
                "longest_trade_duration": timedelta(0),
                "shortest_trade_duration": timedelta(0)
            } for pair in self.frame_with_signals.keys()
        }

        trades_per_coin = group_by(closed_trades, "pair")

        for key, closed_pair_trades in trades_per_coin.items():
            seen_drawdown_per_coin = get_max_seen_drawdown_per_coin(
                self.frame_with_signals[key],
                closed_pair_trades,
                self.config.fee
            )
            per_coin_stats[key]["max_seen_ratio"] = seen_drawdown_per_coin
            realised_drawdown_per_coin = get_max_realised_drawdown_per_coin(
                self.frame_with_signals[key],
                closed_pair_trades,
                self.config.fee
            )

            per_coin_stats[key]["avg_trade_duration"], \
                per_coin_stats[key]["longest_trade_duration"], \
                per_coin_stats[key]["shortest_trade_duration"] = \
                calculate_trade_durations(closed_pair_trades)

            per_coin_stats[key]["max_realised_ratio"] = realised_drawdown_per_coin

        for trade in closed_trades:

            # Update average profit
            per_coin_stats[trade.pair]['cum_profit_prct'] += (trade.profit_ratio - 1) * 100

            # Update total profit percentage and amount
            per_coin_stats[trade.pair]['total_profit_ratio'] = \
                per_coin_stats[trade.pair]['total_profit_ratio'] * trade.profit_ratio

            # Update profit and amount of trades
            per_coin_stats[trade.pair]['total_profit_amount'] += trade.profit_dollar
            per_coin_stats[trade.pair]['amount_of_trades'] += 1
            per_coin_stats[trade.pair]['sell_reasons'][trade.sell_reason] += 1

            # Check for max realised drawdown
            if per_coin_stats[trade.pair]['drawdown_ratio'] < per_coin_stats[trade.pair]['max_realised_ratio']:
                per_coin_stats[trade.pair]['max_realised_ratio'] = per_coin_stats[trade.pair]['drawdown_ratio']

            # Sum total times
            if per_coin_stats[trade.pair]['total_duration'] is None:
                per_coin_stats[trade.pair]['total_duration'] = trade.closed_at - trade.opened_at
            else:
                per_coin_stats[trade.pair]['total_duration'] += trade.closed_at - trade.opened_at
        return per_coin_stats

    def calculate_statistics_for_plots(self, closed_trades, open_trades):

        # Used for plotting
        self.buy_points = {pair: [] for pair in self.frame_with_signals.keys()}
        self.sell_points = {pair: [] for pair in self.frame_with_signals.keys()}

        for trade in closed_trades:
            # Save buy/sell signals
            self.buy_points[trade.pair].append(trade.opened_at)
            self.sell_points[trade.pair].append(trade.closed_at)

        for trade in open_trades:
            # Save buy/sell signals
            self.buy_points[trade.pair].append(trade.opened_at)

    def get_left_open_trades_results(self, open_trades: [Trade]) -> list:
        left_open_trade_stats = []
        for trade in open_trades:
            max_seen_drawdown = get_max_seen_drawdown_per_trade(
                self.frame_with_signals[trade.pair],
                trade,
                self.config.fee
            )
            left_open_trade_results = LeftOpenTradeResult(pair=trade.pair,
                                                          curr_profit_percentage=(trade.profit_ratio - 1) * 100,
                                                          curr_profit=trade.profit_dollar,
                                                          max_seen_drawdown=(max_seen_drawdown - 1) * 100,
                                                          opened_at=trade.opened_at)

            left_open_trade_stats.append(left_open_trade_results)
        return left_open_trade_stats


def get_market_change(ticks: list, pairs: list, data_dict: dict) -> dict:
    market_change = {}
    total_change = 0
    for pair in pairs:
        begin_value = data_dict[pair][ticks[0]]['close']
        end_value = data_dict[pair][ticks[-1]]['close']
        coin_change = end_value / begin_value
        market_change[pair] = coin_change
        total_change += coin_change
    market_change['all'] = total_change / len(pairs) if len(pairs) > 0 else 1
    return market_change
