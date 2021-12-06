from datetime import datetime, timedelta

import numpy as np
from collections import defaultdict

from cli.print_utils import print_info
from modules.output.results import CoinInsights, MainResults, LeftOpenTradeResult
from modules.public.pairs_data import PairsData
from modules.public.trading_stats import TradingStats
from modules.stats.drawdown.drawdown import get_max_drawdown_ratio, get_max_drawdown_ratio_without_buy_rows
from modules.stats.metrics.profit_ratio import get_seen_cum_profit_ratio_per_coin, get_realised_profit_ratio
from modules.stats.drawdown.for_portfolio import get_max_seen_drawdown_for_portfolio, \
    get_max_realised_drawdown_for_portfolio, get_sharpe_ratio, get_sortino_ratio
from modules.stats.drawdown.per_trade import get_max_seen_drawdown_per_trade
from modules.stats.metrics.market_change import get_market_change, get_market_drawdown
from modules.stats.metrics.trades import calculate_best_worst_trade, get_number_of_losing_trades, \
    get_number_of_consecutive_losing_trades, calculate_trade_durations
from modules.stats.metrics.winning_weeks import get_winning_weeks_per_coin, \
    get_winning_weeks_for_portfolio
from modules.stats.stats_config import StatsConfig
from modules.stats.trade import Trade, SellReason
from modules.stats.tradingmodule import TradingModule

from utils.dict import group_by
from utils.utils import calculate_worth_of_open_trades


class StatsModule:

    def __init__(self, config: StatsConfig, frame_with_signals: PairsData, trading_module: TradingModule, df):
        self.buy_points = None
        self.sell_points = None
        self.df = df
        self.config = config
        self.trading_module = trading_module
        self.frame_with_signals = frame_with_signals

        if self.config.stoploss_type == 'standard':
            self.config.stoploss_type = 'static'

    def analyze(self) -> TradingStats:
        pairs = list(self.frame_with_signals.keys())
        ticks = list(self.frame_with_signals[pairs[0]].keys()) if pairs else []
        print_info("Backtesting")
        for tick in ticks:
            for pair in pairs:
                pair_dict = self.frame_with_signals[pair]
                tick_dict = pair_dict[tick]
                self.trading_module.tick(tick_dict, pair_dict)

        market_change = get_market_change(self.df, pairs, self.frame_with_signals)
        market_drawdown = get_market_drawdown(pairs, self.frame_with_signals)
        return self.generate_backtesting_result(market_change, market_drawdown)

    def generate_backtesting_result(self, market_change: dict, market_drawdown: dict) -> TradingStats:
        coin_results, market_change_weekly = self.generate_coin_results(self.trading_module.closed_trades,
                                                                        market_change,
                                                                        market_drawdown)
        best_trade_ratio, best_trade_pair, worst_trade_ratio, worst_trade_pair = \
            calculate_best_worst_trade(self.trading_module.closed_trades)
        open_trade_results = self.get_left_open_trades_results(self.trading_module.open_trades)

        main_results = self.generate_main_results(
            self.trading_module.open_trades,
            self.trading_module.closed_trades,
            self.trading_module.budget,
            market_change,
            market_drawdown,
            best_trade_ratio,
            best_trade_pair,
            worst_trade_ratio,
            worst_trade_pair,
            market_change_weekly)
        self.calculate_statistics_for_plots(self.trading_module.closed_trades, self.trading_module.open_trades)

        return TradingStats(
            main_results=main_results,
            coin_results=coin_results,
            open_trade_results=open_trade_results,
            frame_with_signals=self.frame_with_signals,
            buypoints=self.buy_points,
            sellpoints=self.sell_points,
            df=self.df,
            trades=self.trading_module.open_trades + self.trading_module.closed_trades,
            capital_per_timestamp=self.trading_module.capital_per_timestamp
        )

    def generate_main_results(self, open_trades: [Trade], closed_trades: [Trade], budget: float,
                              market_change: dict, market_drawdown: dict, best_trade_ratio: float,
                              best_trade_pair: str, worst_trade_ratio: float,
                              worst_trade_pair: str, market_change_weekly: dict) -> MainResults:
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

        sharpe_ratio = get_sharpe_ratio(self.trading_module.capital_per_timestamp)

        sortino_ratio = get_sortino_ratio(self.trading_module.capital_per_timestamp)

        # Find amount of winning, draw and losing weeks for portfolio
        win_weeks, draw_weeks, loss_weeks = get_winning_weeks_for_portfolio(
            self.trading_module.capital_per_timestamp,
            market_change_weekly
        )

        nr_losing_trades = get_number_of_losing_trades(closed_trades)
        nr_consecutive_losing_trades = get_number_of_consecutive_losing_trades(closed_trades)

        best_trade_profit_percentage = (best_trade_ratio - 1) * 100 \
            if best_trade_ratio != -np.inf else 0
        worst_trade_profit_percentage = (worst_trade_ratio - 1) * 100 \
            if worst_trade_ratio != np.inf else 0

        avg_trade_duration, longest_trade_duration, shortest_trade_duration = \
            calculate_trade_durations(closed_trades)

        tested_from = datetime.fromtimestamp(self.config.backtesting_from / 1000)
        tested_to = datetime.fromtimestamp(self.config.backtesting_to / 1000)

        timespan_seconds = (tested_to - tested_from).total_seconds()
        nr_days = timespan_seconds / timedelta(days=1).total_seconds()

        return MainResults(tested_from=tested_from,
                           tested_to=tested_to,
                           timeframe=self.config.timeframe,
                           strategy_name=self.config.strategy_name,
                           max_open_trades=self.config.max_open_trades,
                           exposure_per_trade=self.config.exposure_per_trade,
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
                           max_realised_drawdown=(max_realised_drawdown - 1) * 100,
                           worst_trade_profit_percentage=worst_trade_profit_percentage,
                           worst_trade_pair=worst_trade_pair,
                           best_trade_profit_percentage=best_trade_profit_percentage,
                           best_trade_pair=best_trade_pair,
                           avg_trade_duration=avg_trade_duration,
                           longest_trade_duration=longest_trade_duration,
                           shortest_trade_duration=shortest_trade_duration,
                           win_weeks=win_weeks,
                           draw_weeks=draw_weeks,
                           loss_weeks=loss_weeks,
                           max_seen_drawdown=(max_seen_drawdown['drawdown'] - 1) * 100,
                           drawdown_from=max_seen_drawdown['from'],
                           drawdown_to=max_seen_drawdown['to'],
                           drawdown_at=max_seen_drawdown['at'],
                           stoploss=self.config.stoploss,
                           stoploss_type=self.config.stoploss_type,
                           fee=self.config.fee,
                           total_fee_amount=self.trading_module.total_fee_paid,
                           rejected_buy_signal=self.trading_module.rejected_buy_signal,
                           sharpe_ratio=sharpe_ratio,
                           sortino_ratio=sortino_ratio)

    def generate_coin_results(self, closed_trades: [Trade], market_change: dict, market_drawdown: dict) -> [list, dict]:
        stats, market_change_weekly = self.calculate_statistics_per_coin(closed_trades)
        new_stats = []

        for coin in stats:
            avg_profit_prct = (stats[coin]['cum_profit_prct'] / stats[coin]['amount_of_trades']) \
                if stats[coin]['amount_of_trades'] > 0 else 0

            coin_insight = CoinInsights(pair=coin,
                                        n_trades=stats[coin]['amount_of_trades'],
                                        n_wins=stats[coin]['amount_of_winning_trades'],
                                        n_losses=stats[coin]['amount_of_losing_trades'],
                                        market_change=(market_change[coin] - 1) * 100,
                                        market_drawdown=(market_drawdown[coin] - 1) * 100,
                                        cum_profit_percentage=stats[coin]['cum_profit_prct'],
                                        total_profit_percentage=(stats[coin]['total_profit_ratio'] - 1) * 100,
                                        avg_profit_percentage=avg_profit_prct,
                                        profit=stats[coin]['total_profit_amount'],
                                        max_seen_drawdown=(stats[coin]['max_seen_ratio'] - 1) * 100,
                                        max_realised_drawdown=(stats[coin]['max_realised_ratio'] - 1) * 100,
                                        win_weeks=stats[coin]['win_weeks'],
                                        draw_weeks=stats[coin]['draw_weeks'],
                                        loss_weeks=stats[coin]['loss_weeks'],
                                        avg_trade_duration=stats[coin]['avg_trade_duration'],
                                        longest_trade_duration=stats[coin]['longest_trade_duration'],
                                        shortest_trade_duration=stats[coin]['shortest_trade_duration'],
                                        roi=stats[coin]['sell_reasons'][SellReason.ROI],
                                        stoploss=stats[coin]['sell_reasons'][SellReason.STOPLOSS],
                                        sell_signal=stats[coin]['sell_reasons'][SellReason.SELL_SIGNAL])
            new_stats.append(coin_insight)

        return new_stats, market_change_weekly

    def calculate_statistics_per_coin(self, closed_trades):
        per_coin_stats = {
            pair: {
                'cum_profit_prct': 0,
                'total_profit_ratio': 1.0,
                'total_profit_amount': 0.0,
                'amount_of_trades': 0,
                'amount_of_winning_trades': 0,
                'amount_of_losing_trades': 0,
                'peak_ratio': 1.0,
                'drawdown_ratio': 1.0,
                'total_ratio': 1.0,
                'max_seen_ratio': 1.0,
                'max_realised_ratio': 1.0,
                'total_duration': None,
                'sell_reasons': defaultdict(int),
                "avg_trade_duration": timedelta(0),
                "longest_trade_duration": timedelta(0),
                "shortest_trade_duration": timedelta(0),
                "win_weeks": 0,
                "draw_weeks": 0,
                "loss_weeks": 0
            } for pair in self.frame_with_signals.keys()
        }
        market_change_weekly = {pair: None for pair in self.frame_with_signals.keys()}
        trades_per_coin = group_by(closed_trades, "pair")

        print_info("Calculating statistics")
        for key, closed_pair_trades in trades_per_coin.items():
            # Calculate max seen drawdown ratio
            seen_cum_profit_ratio_df = get_seen_cum_profit_ratio_per_coin(
                self.frame_with_signals[key],
                closed_pair_trades,
                self.config.fee
            )
            per_coin_stats[key]["max_seen_ratio"] = get_max_drawdown_ratio(seen_cum_profit_ratio_df)

            # Calculate max realised drawdown ratio
            realised_cum_profit_ratio_df = get_realised_profit_ratio(
                self.frame_with_signals[key],
                closed_pair_trades,
                self.config.fee,
            )
            per_coin_stats[key]["max_realised_ratio"] = \
                get_max_drawdown_ratio_without_buy_rows(realised_cum_profit_ratio_df)

            # Find avg, longest and shortest trade durations
            per_coin_stats[key]["avg_trade_duration"], \
            per_coin_stats[key]["longest_trade_duration"], \
            per_coin_stats[key]["shortest_trade_duration"] = \
                calculate_trade_durations(closed_pair_trades)

            # Find winning, draw and losing weeks for current coin
            per_coin_stats[key]["win_weeks"], \
            per_coin_stats[key]["draw_weeks"], \
            per_coin_stats[key]["loss_weeks"], \
            market_change_weekly[key] = get_winning_weeks_per_coin(
                self.frame_with_signals[key],
                seen_cum_profit_ratio_df
            )

            for trade in closed_pair_trades:
                # Update average profit
                per_coin_stats[key]['cum_profit_prct'] += (trade.profit_ratio - 1) * 100

                # Update total profit percentage and amount
                per_coin_stats[key]['total_profit_ratio'] = \
                    per_coin_stats[key]['total_profit_ratio'] * trade.profit_ratio

                # Update profit and amount of trades
                per_coin_stats[key]['total_profit_amount'] += trade.profit_dollar
                per_coin_stats[key]['amount_of_trades'] += 1
                if trade.profit_ratio > 1:
                    per_coin_stats[key]['amount_of_winning_trades'] += 1
                if trade.profit_ratio < 1:
                    per_coin_stats[key]['amount_of_losing_trades'] += 1
                per_coin_stats[key]['sell_reasons'][trade.sell_reason] += 1

                # Check for max realised drawdown
                if per_coin_stats[key]['drawdown_ratio'] < per_coin_stats[key]['max_realised_ratio']:
                    per_coin_stats[key]['max_realised_ratio'] = per_coin_stats[key]['drawdown_ratio']

                # Sum total times
                if per_coin_stats[key]['total_duration'] is None:
                    per_coin_stats[key]['total_duration'] = trade.closed_at - trade.opened_at
                else:
                    per_coin_stats[key]['total_duration'] += trade.closed_at - trade.opened_at
        return per_coin_stats, market_change_weekly

    def calculate_statistics_for_plots(self, closed_trades, open_trades):
        # Used for plotting
        self.buy_points = {pair: {} for pair in self.frame_with_signals.keys()}
        self.sell_points = {pair: {} for pair in self.frame_with_signals.keys()}

        for trade in closed_trades:
            # Save buy/sell signals
            self.buy_points[trade.pair][trade.opened_at] = trade.open
            self.sell_points[trade.pair][trade.closed_at] = trade.close

        for trade in open_trades:
            # Save buy/sell signals
            self.buy_points[trade.pair][trade.opened_at] = trade.open

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
