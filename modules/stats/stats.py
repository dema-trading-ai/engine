from collections import defaultdict
from datetime import datetime, timedelta
from tqdm import tqdm
import numpy as np

from modules.output.results import CoinInsights, MainResults, OpenTradeResult
from modules.pairs_data import PairsData
from modules.stats.stats_config import StatsConfig
from modules.stats.trade import Trade, SellReason
from modules.stats.trading_stats import TradingStats
from modules.stats.tradingmodule import TradingModule
from utils import calculate_worth_of_open_trades


def generate_open_trades_results(open_trades: [Trade]) -> list:
    open_trade_stats = []
    for trade in open_trades:
        open_trade_res = OpenTradeResult(pair=trade.pair,
                                         curr_profit_percentage=(trade.profit_ratio - 1) * 100,
                                         curr_profit=trade.profit_dollar,
                                         max_seen_drawdown=(trade.max_seen_drawdown - 1) * 100,
                                         opened_at=trade.opened_at)

        open_trade_stats.append(open_trade_res)
    return open_trade_stats


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


class StatsModule:
    buypoints = None
    sellpoints = None

    def __init__(self, config: StatsConfig, frame_with_signals: PairsData, trading_module: TradingModule, df):
        self.df = df
        self.config = config
        self.trading_module = trading_module
        self.frame_with_signals = frame_with_signals

    def analyze(self) -> TradingStats:
        pairs = list(self.frame_with_signals.keys())
        ticks = list(self.frame_with_signals[pairs[0]].keys())

        for tick in tqdm(ticks, desc='[INFO] Backtesting', total=len(ticks), ncols=75):
            for pair in pairs:
                pair_dict = self.frame_with_signals[pair]
                tick_dict = pair_dict[tick]
                self.trading_module.tick(tick_dict, pair_dict)

        market_change = get_market_change(ticks, pairs, self.frame_with_signals)
        return self.generate_backtesting_result(market_change)

    def generate_backtesting_result(self,
                                    market_change: dict) -> TradingStats:

        trading_module = self.trading_module
        coin_res = self.generate_coin_results(trading_module.closed_trades, market_change)
        best_trade_ratio, best_trade_pair, worst_trade_ratio, worst_trade_pair = \
            calculate_best_worst_trade(trading_module.closed_trades)
        open_trade_res = generate_open_trades_results(trading_module.open_trades)
        main_results = self.generate_main_results(
            trading_module.open_trades,
            trading_module.closed_trades,
            trading_module.budget,
            market_change,
            best_trade_ratio,
            best_trade_pair,
            worst_trade_ratio,
            worst_trade_pair)
        self.calculate_statistics_for_plots(trading_module.closed_trades, trading_module.open_trades)

        return TradingStats(
            main_results=main_results,
            coin_res=coin_res,
            open_trade_res=open_trade_res,
            frame_with_signals=self.frame_with_signals,
            buypoints=self.buypoints,
            sellpoints=self.sellpoints,
            df=self.df,
            trades=trading_module.open_trades + trading_module.closed_trades
        )

    def generate_main_results(self, open_trades: [Trade], closed_trades: [Trade], budget: float,
                              market_change: dict, best_trade_ratio: float,
                              best_trade_pair: str, worst_trade_ratio: float,
                              worst_trade_pair: str) -> MainResults:
        # Get total budget and calculate overall profit
        budget += calculate_worth_of_open_trades(open_trades)
        overall_profit_percentage = ((budget - self.config.starting_capital) / self.config.starting_capital) * 100

        # Find max seen and realised drawdown
        max_seen_drawdown = self.calculate_max_seen_drawdown()
        max_realised_drawdown = self.calculate_max_realised_drawdown()

        # Update variables for prettier terminal output
        drawdown_from = datetime.fromtimestamp(max_seen_drawdown['from'] / 1000).strftime('%Y-%m-%d ''%H:%M') \
            if max_seen_drawdown['from'] != 0 else '-'
        drawdown_to = datetime.fromtimestamp(max_seen_drawdown['to'] / 1000).strftime('%Y-%m-%d ''%H:%M') \
            if max_seen_drawdown['to'] != 0 else '-'
        drawdown_at = datetime.fromtimestamp(max_seen_drawdown['at'] / 1000).strftime('%Y-%m-%d ''%H:%M') \
            if max_seen_drawdown['at'] != 0 else '-'
        best_trade_profit_percentage = (best_trade_ratio - 1) * 100 \
            if best_trade_ratio != -np.inf else 0
        worst_trade_profit_percentage = (worst_trade_ratio - 1) * 100 \
            if worst_trade_ratio != np.inf else 0

        tested_from = datetime.fromtimestamp(self.config.backtesting_from / 1000)
        tested_from_string = tested_from.strftime('%Y-%m-%d ''%H:%M')
        tested_to = datetime.fromtimestamp(
            self.config.backtesting_to / 1000)
        tested_to_string = tested_to.strftime('%Y-%m-%d ''%H:%M')

        timespan_seconds = (tested_to - tested_from).total_seconds()
        nr_days = timespan_seconds / timedelta(days=1).total_seconds()

        return MainResults(tested_from=tested_from_string,
                           tested_to=tested_to_string,
                           max_open_trades=self.config.max_open_trades,
                           market_change_coins=(market_change['all'] - 1) * 100,
                           market_change_btc=(self.config.btc_marketchange_ratio - 1) * 100,
                           starting_capital=self.config.starting_capital,
                           end_capital=budget,
                           overall_profit_percentage=overall_profit_percentage,
                           n_trades=len(open_trades) + len(closed_trades),
                           n_average_trades=(len(open_trades) + len(closed_trades)) / nr_days,
                           n_left_open_trades=len(open_trades),
                           n_trades_with_loss=max_realised_drawdown['drawdown_trades'],
                           n_consecutive_losses=max_realised_drawdown['max_consecutive_losses'],
                           max_realised_drawdown=(max_realised_drawdown['max_drawdown'] - 1) * 100,
                           worst_trade_profit_percentage=worst_trade_profit_percentage,
                           worst_trade_pair=worst_trade_pair,
                           best_trade_profit_percentage=best_trade_profit_percentage,
                           best_trade_pair=best_trade_pair,
                           max_seen_drawdown=(max_seen_drawdown["drawdown"] - 1) * 100,
                           drawdown_from=drawdown_from,
                           drawdown_to=drawdown_to,
                           drawdown_at=drawdown_at,
                           stoploss=self.config.stoploss,
                           stoploss_type=self.config.stoploss_type,
                           fee=self.config.fee,
                           total_fee_amount=self.trading_module.total_fee_paid)

    def generate_coin_results(self, closed_trades: [Trade], market_change: dict) -> [list, dict]:
        stats = self.calculate_statistics_per_coin(closed_trades)
        new_stats = []

        for coin in stats:
            # Update variables for prettier terminal output
            avg_profit_perc = (stats[coin]['cum_profit_prct'] / stats[coin]['amount_of_trades']) \
                if stats[coin]['amount_of_trades'] > 0 else 0
            avg_trade_duration = (stats[coin]['total_duration'] / stats[coin]['amount_of_trades']) \
                if stats[coin]['amount_of_trades'] > 0 else '-'

            coin_insight = CoinInsights(pair=coin,
                                        n_trades=stats[coin]['amount_of_trades'],
                                        market_change=(market_change[coin] - 1) * 100,
                                        cum_profit_percentage=stats[coin]['cum_profit_prct'],
                                        total_profit_percentage=(stats[coin]['total_profit_ratio'] - 1) * 100,
                                        avg_profit_percentage=avg_profit_perc,
                                        profit=stats[coin]['total_profit_amount'],
                                        max_seen_drawdown=(stats[coin]['max_seen_ratio'] - 1) * 100,
                                        max_realised_drawdown=(stats[coin]['max_realised_ratio'] - 1) * 100,
                                        avg_trade_duration=avg_trade_duration,
                                        roi=stats[coin]['sell_reasons'][SellReason.ROI],
                                        stoploss=stats[coin]['sell_reasons'][SellReason.STOPLOSS],
                                        sell_signal=stats[coin]['sell_reasons'][SellReason.SELL_SIGNAL])
            new_stats.append(coin_insight)

        return new_stats

    def calculate_statistics_per_coin(self, closed_trades):
        trades_per_coin = {
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
                'sell_reasons': defaultdict(int)
            } for pair in self.frame_with_signals.keys()
        }

        for trade in closed_trades:

            # Update average profit
            trades_per_coin[trade.pair]['cum_profit_prct'] += (trade.profit_ratio - 1) * 100

            # Update total profit percentage and amount
            trades_per_coin[trade.pair]['total_profit_ratio'] = \
                trades_per_coin[trade.pair]['total_profit_ratio'] * trade.profit_ratio

            # Update profit and amount of trades
            trades_per_coin[trade.pair]['total_profit_amount'] += trade.profit_dollar
            trades_per_coin[trade.pair]['amount_of_trades'] += 1
            trades_per_coin[trade.pair]['sell_reasons'][trade.sell_reason] += 1

            # Check for max seen drawdown
            max_seen_drawdown_ratio = trades_per_coin[trade.pair]['drawdown_ratio'] * trade.max_seen_drawdown
            if max_seen_drawdown_ratio < trades_per_coin[trade.pair]['max_seen_ratio']:
                trades_per_coin[trade.pair]['max_seen_ratio'] = max_seen_drawdown_ratio

            # Update curr and total ratio
            trades_per_coin[trade.pair]['drawdown_ratio'] *= trade.profit_ratio
            trades_per_coin[trade.pair]['total_ratio'] *= trade.profit_ratio

            # Check for max realised drawdown
            if trades_per_coin[trade.pair]['drawdown_ratio'] < trades_per_coin[trade.pair]['max_realised_ratio']:
                trades_per_coin[trade.pair]['max_realised_ratio'] = trades_per_coin[trade.pair]['drawdown_ratio']

            # Check for new ratio high
            if trades_per_coin[trade.pair]['total_ratio'] > trades_per_coin[trade.pair]['peak_ratio']:
                trades_per_coin[trade.pair]['peak_ratio'] = trades_per_coin[trade.pair]['total_ratio']
                trades_per_coin[trade.pair]['drawdown_ratio'] = 1.0  # reset ratio

            # Sum total times
            if trades_per_coin[trade.pair]['total_duration'] is None:
                trades_per_coin[trade.pair]['total_duration'] = trade.closed_at - trade.opened_at
            else:
                trades_per_coin[trade.pair]['total_duration'] += trade.closed_at - trade.opened_at
        return trades_per_coin

    # Method for calculating max seen drawdown
    # Max seen = visual drawdown (if you plot it). This drawdown might not be realised.

    def calculate_max_seen_drawdown(self) -> dict:
        """
        Method calculates max seen drawdown based on the saved budget / value changes
        :return: returns max_seen_drawdown as a dictionary
        :rtype: dictionary
        """
        max_seen_drawdown = {
            "from": 0,
            "to": 0,
            "at": 0,
            "drawdown": 1,  # ratio
            "peak": 0,
            "bottom": 0
        }
        temp_seen_drawdown = max_seen_drawdown.copy() 

        # Find dictionaries with capital info at certain ticks (open trades + budget)
        lowest_total_capital_open_trades_at_tick = self.trading_module.lowest_total_capital_open_trades
        highest_total_capital_open_trades_at_tick = self.trading_module.highest_total_capital_open_trades
        total_budget_at_tick = self.trading_module.budget_per_timestamp

        # Find ticks for total capital (low/max) of open trades
        open_trade_ticks = list(lowest_total_capital_open_trades_at_tick.keys())

        # Find ticks for total budget
        budget_ticks = list(total_budget_at_tick.keys())

        # Combine all possible ticks
        ticks = open_trade_ticks + budget_ticks
        ticks.sort()

        for tick in ticks:
            # Find lowest and maximum capital at tick
            lowest_portfolio = lowest_total_capital_open_trades_at_tick.get(tick, 0) \
                + total_budget_at_tick.get(tick,0)
            maximum_portfolio = highest_total_capital_open_trades_at_tick.get(tick, 0) \
                + total_budget_at_tick.get(tick, 0)

            # Check for new drawdown period
            if maximum_portfolio > temp_seen_drawdown['peak']:
                # If last drawdown was larger than max drawdown, update max drawdown
                if temp_seen_drawdown['drawdown'] < max_seen_drawdown['drawdown']:
                    max_seen_drawdown = temp_seen_drawdown.copy()

                # Reset temp_seen_drawdown stats
                temp_seen_drawdown['peak'] = maximum_portfolio
                temp_seen_drawdown['bottom'] = maximum_portfolio
                temp_seen_drawdown['drawdown'] = 1.0  # ratio w/ respect to peak
                temp_seen_drawdown['from'] = tick

            # Check if drawdown reached new bottom
            if lowest_portfolio < temp_seen_drawdown['bottom']:
                temp_seen_drawdown['bottom'] = lowest_portfolio
                temp_seen_drawdown['drawdown'] = temp_seen_drawdown['bottom'] / temp_seen_drawdown['peak']
                temp_seen_drawdown['at'] = tick

            # Update drawdown period
            temp_seen_drawdown['to'] = tick

        # If last drawdown was larger than max drawdown, update max drawdown
        if temp_seen_drawdown['drawdown'] < max_seen_drawdown['drawdown']:
            max_seen_drawdown = temp_seen_drawdown.copy()
        return max_seen_drawdown

    def calculate_max_realised_drawdown(self) -> dict:
        """
        Method calculates max seen drawdown based on the saved budget / value changes
        :return: returns max_seen_drawdown as a dictionary
        :rtype: dictionary
        """
        max_realised_drawdown = {
            "total_ratio": 1,
            "peak_ratio": 1,
            "curr_drawdown": 1,  # ratio
            "max_drawdown": 1,  # ratio
            "curr_consecutive_losses": 0,
            "max_consecutive_losses": 0,
            "drawdown_trades": 0
        }

        realised_profits = self.trading_module.realised_profits
        prev_profit = self.config.starting_capital

        for new_profit in realised_profits:
            profit_ratio = new_profit / prev_profit

            # Update consecutive losses
            if profit_ratio < 1:
                max_realised_drawdown['curr_consecutive_losses'] += 1
                max_realised_drawdown['drawdown_trades'] += 1
            else:
                max_realised_drawdown['curr_consecutive_losses'] = 0

            # Check if max consecutive losses is beaten
            if max_realised_drawdown['curr_consecutive_losses'] > max_realised_drawdown['max_consecutive_losses']:
                max_realised_drawdown['max_consecutive_losses'] = max_realised_drawdown['curr_consecutive_losses']

            # Update curr and total ratio
            max_realised_drawdown['curr_drawdown'] *= profit_ratio
            max_realised_drawdown['total_ratio'] *= profit_ratio

            # Check for max realised drawdown
            if max_realised_drawdown['curr_drawdown'] < max_realised_drawdown['max_drawdown']:
                max_realised_drawdown['max_drawdown'] = max_realised_drawdown['curr_drawdown']

            # Check for new ratio high
            if max_realised_drawdown['total_ratio'] > max_realised_drawdown['peak_ratio']:
                max_realised_drawdown['peak_ratio'] = max_realised_drawdown['total_ratio']
                max_realised_drawdown['curr_drawdown'] = 1.0  # reset ratio

            prev_profit = new_profit

        return max_realised_drawdown

    def calculate_statistics_for_plots(self, closed_trades, open_trades):

        # Used for plotting
        self.buypoints = {pair: [] for pair in self.frame_with_signals.keys()}
        self.sellpoints = {pair: [] for pair in self.frame_with_signals.keys()}

        for trade in closed_trades:
            # Save buy/sell signals
            self.buypoints[trade.pair].append(trade.opened_at)
            self.sellpoints[trade.pair].append(trade.closed_at)

        for trade in open_trades:
            # Save buy/sell signals
            self.buypoints[trade.pair].append(trade.opened_at)


def get_market_change(ticks: list, pairs: list, data_dict: dict) -> dict:
    """
    Calculates the market change for every coin if bought at start and sold at end.

    :param ticks: list with all ticks
    :type ticks: list
    :param pairs: list of traded pairs
    :type pairs: list
    :param data_dict: dict containing OHLCV data per pair
    :type data_dict: dict
    :return: dict with market change per pair
    :rtype: dict
    """
    market_change = {}
    total_change = 0
    for pair in pairs:
        begin_value = data_dict[pair][ticks[0]]['close']
        end_value = data_dict[pair][ticks[-1]]['close']
        coin_change = end_value / begin_value
        market_change[pair] = coin_change
        total_change += coin_change
    market_change['all'] = total_change / len(pairs)
    return market_change
