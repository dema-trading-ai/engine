from datetime import datetime, timedelta
from tqdm import tqdm
import numpy as np

from modules.output.results import CoinInsights, MainResults, OpenTradeResult
from modules.pairs_data import PairsData
from modules.stats.drawdown.per_coin import get_max_seen_drawdown_per_coin
from modules.stats.drawdown.for_portfolio import get_max_seen_drawdown_for_portfolio
from modules.stats.drawdown.per_trade import get_max_seen_drawdown_per_trade
from modules.stats.stats_config import StatsConfig
from modules.stats.trade import Trade, SellReason
from modules.stats.trading_stats import TradingStats
from modules.stats.tradingmodule import TradingModule
from collections import defaultdict

from utils.dict import group_by
from utils.utils import calculate_worth_of_open_trades



def calculate_best_worst_trade(closed_trades):
    if len(closed_trades) > 0:
        best_trade_ratio = max(closed_trades, key=lambda trade: trade.profit_ratio, default=-np.inf).profit_ratio
        worst_trade_ratio = min(closed_trades, key=lambda trade: trade.profit_ratio, default=np.inf).profit_ratio
    else:
        best_trade_ratio = -np.inf
        worst_trade_ratio = np.inf

    return best_trade_ratio, worst_trade_ratio


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
        best_trade_ratio, worst_trade_ratio = calculate_best_worst_trade(trading_module.closed_trades)
        open_trade_res = self.generate_open_trades_results(trading_module.open_trades)
        main_results = self.generate_main_results(
            trading_module.open_trades,
            trading_module.closed_trades,
            trading_module.budget,
            market_change,
            best_trade_ratio,
            worst_trade_ratio)
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
                              market_change: dict, best_trade_ratio: float, worst_trade_ratio: float) -> MainResults:
        # Get total budget and calculate overall profit
        budget += calculate_worth_of_open_trades(open_trades)
        overall_profit_percentage = ((budget - self.config.starting_capital) / self.config.starting_capital) * 100

        # Find max seen and realised drawdown
        max_realised_drawdown = self.calculate_max_realised_drawdown()

        max_seen_drawdown = get_max_seen_drawdown_for_portfolio(self.trading_module.capital_per_timestamp)

        best_trade_profit_percentage = (best_trade_ratio - 1) * 100 \
            if best_trade_ratio != -np.inf else 0
        worst_trade_profit_percentage = (worst_trade_ratio - 1) * 100 \
            if worst_trade_ratio != np.inf else 0

        tested_from = datetime.fromtimestamp(self.config.backtesting_from / 1000)
        tested_to = datetime.fromtimestamp(self.config.backtesting_to / 1000)

        timespan_seconds = (tested_to - tested_from).total_seconds()
        nr_days = timespan_seconds / timedelta(days=1).total_seconds()

        return MainResults(tested_from=tested_from,
                           tested_to=tested_to,
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
                           best_trade_profit_percentage=best_trade_profit_percentage,
                           max_seen_drawdown=(max_seen_drawdown['drawdown']-1) * 100,
                           drawdown_from=max_seen_drawdown['from'],
                           drawdown_to=max_seen_drawdown['to'],
                           drawdown_at=max_seen_drawdown['at'],
                           configured_stoploss=self.config.stoploss,
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
                'sell_reasons': defaultdict(int)
            } for pair in self.frame_with_signals.keys()
        }

        trades_per_coin = group_by(closed_trades, "pair")

        for key, closed_pair_trades in trades_per_coin.items():
            drawdown_per_coin = get_max_seen_drawdown_per_coin(self.frame_with_signals[key], closed_pair_trades, self.config.fee)
            per_coin_stats[key]["max_seen_ratio"] = drawdown_per_coin

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

    def generate_open_trades_results(self, open_trades: [Trade]) -> list:
        open_trade_stats = []
        for trade in open_trades:
            max_seen_drawdown = get_max_seen_drawdown_per_trade(self.frame_with_signals[trade.pair], trade, self.config.fee)
            open_trade_res = OpenTradeResult(pair=trade.pair,
                                             curr_profit_percentage=(trade.profit_ratio - 1) * 100,
                                             curr_profit=trade.profit_dollar,
                                             max_seen_drawdown=(max_seen_drawdown - 1) * 100,
                                             opened_at=trade.opened_at)

            open_trade_stats.append(open_trade_res)
        return open_trade_stats


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
