import random
from collections import defaultdict
from datetime import datetime, timedelta

from cli.print_utils import print_info
from modules.output.results import CoinInsights, MainResults, LeftOpenTradeResult
from modules.public.pairs_data import PairsData
from modules.public.trading_stats import TradingStats
from modules.setup import ConfigModule
from modules.stats.drawdown.drawdown import get_max_drawdown_ratio, get_max_drawdown_ratio_without_buy_rows
from modules.stats.drawdown.for_portfolio import get_max_seen_drawdown_for_portfolio, \
    get_max_realised_drawdown_for_portfolio, get_longest_drawdown
from modules.stats.drawdown.per_trade import get_max_seen_drawdown_per_trade
from modules.stats.metrics.market_change import get_market_change, get_market_drawdown
from modules.stats.metrics.profit_ratio import get_realised_profit_ratio, get_seen_cum_profit_ratio, \
    get_profit_ratio_from_capital
from modules.stats.metrics.trades import compute_trade_rankings, get_number_of_losing_trades, \
    get_number_of_consecutive_losing_trades, calculate_trade_durations, compute_risk_reward_ratio, \
    compute_volume_turnover
from modules.stats.metrics.winning_weeks import get_profitable_timeframe, get_outperforming_timeframe, get_market_ratios
from modules.stats.ratios.for_portfolio import get_sharpe_sortino_ratios
from modules.stats.trade import Trade, SellReason
from modules.stats.tradingmodule import TradingModule
from utils.dict import group_by
from utils.utils import calculate_worth_of_open_trades


class StatsModule:

    def __init__(self, config: ConfigModule, frame_with_signals: PairsData, trading_module: TradingModule, df):
        self.buy_points = None
        self.sell_points = None
        self.df = df
        self.config = config
        self.trading_module = trading_module
        self.frame_with_signals = frame_with_signals
        self.market_ratio_df = None

        if self.config.stoploss_type == 'standard':
            self.config.stoploss_type = 'static'

    def analyze(self) -> TradingStats:
        pairs = list(self.frame_with_signals.keys())
        ticks = list(self.frame_with_signals[pairs[0]].keys()) if pairs else []
        print_info("Backtesting")
        shuffle = self.config.randomize_pair_order
        for tick in ticks:
            if shuffle:
                random.shuffle(pairs)
            for pair in pairs:
                pair_dict = self.frame_with_signals[pair]
                tick_dict = pair_dict[tick]
                self.trading_module.tick(tick_dict)

        market_change = get_market_change(self.df, pairs, self.frame_with_signals)
        market_drawdown = get_market_drawdown(pairs, self.frame_with_signals)
        return self.generate_backtesting_result(market_change, market_drawdown, pairs)

    def generate_backtesting_result(self, market_change: dict, market_drawdown: dict, pairs: list) -> TradingStats:
        self.market_ratio_df = get_market_ratios(self.frame_with_signals)

        coin_results = self.generate_coin_results(
            self.trading_module.closed_trades,
            market_change,
            market_drawdown,
            pairs)

        open_trade_results = self.get_left_open_trades_results(self.trading_module.open_trades)

        main_results = self.generate_main_results(
            self.trading_module.open_trades,
            self.trading_module.closed_trades,
            self.trading_module.budget,
            market_change,
            market_drawdown
        )
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
                              market_change: dict, market_drawdown: dict) -> MainResults:
        budget += calculate_worth_of_open_trades(open_trades)
        overall_profit_ratio = (budget - self.config.starting_capital) / self.config.starting_capital

        max_realised_drawdown = \
            get_max_realised_drawdown_for_portfolio(self.trading_module.realised_profits_per_timestamp)
        max_seen_drawdown = get_max_seen_drawdown_for_portfolio(self.trading_module.capital_per_timestamp)

        longest_realised_drawdown = get_longest_drawdown(self.trading_module.realised_profits_per_timestamp)

        longest_seen_drawdown = get_longest_drawdown(self.trading_module.capital_per_timestamp)

        sharpe_90d, sortino_90d, sharpe_3y, sortino_3y = \
            get_sharpe_sortino_ratios(
                self.trading_module.capital_per_timestamp)

        profit_ratio_per_timestamp = get_profit_ratio_from_capital(self.trading_module.capital_per_timestamp)
        prof_weeks_win, prof_weeks_draw, prof_weeks_loss = get_profitable_timeframe(
            profit_ratio_per_timestamp,
            "W"
        )
        prof_months_win, prof_months_draw, prof_months_loss = get_profitable_timeframe(
            profit_ratio_per_timestamp,
            "M"
        )
        perf_weeks_win, perf_weeks_draw, perf_weeks_loss = get_outperforming_timeframe(
            profit_ratio_per_timestamp,
            self.market_ratio_df['avg_market_ratio'],
            "W"
        )
        perf_months_win, perf_months_draw, perf_months_loss = get_outperforming_timeframe(
            profit_ratio_per_timestamp,
            self.market_ratio_df['avg_market_ratio'],
            "M"
        )

        nr_losing_trades = get_number_of_losing_trades(closed_trades)
        nr_consecutive_losing_trades, dates_consecutive_losing_trades = \
            get_number_of_consecutive_losing_trades(closed_trades)

        risk_reward_ratio = compute_risk_reward_ratio(closed_trades)

        volume_turnover = compute_volume_turnover(closed_trades, self.config.backtesting_duration)

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
                           market_change_coins=market_change['all'],
                           market_drawdown_coins=market_drawdown['all'],
                           market_change_btc=self.config.btc_marketchange_ratio,
                           market_drawdown_btc=self.config.btc_drawdown_ratio,
                           starting_capital=self.config.starting_capital,
                           end_capital=budget,
                           overall_profit_ratio=overall_profit_ratio,
                           n_trades=len(closed_trades),
                           n_average_trades=len(closed_trades) / nr_days,
                           n_left_open_trades=len(open_trades),
                           n_trades_with_loss=nr_losing_trades,
                           n_consecutive_losses=nr_consecutive_losing_trades,
                           dates_consecutive_losing_trades=dates_consecutive_losing_trades,
                           max_realised_drawdown=max_realised_drawdown,
                           avg_trade_duration=avg_trade_duration,
                           longest_trade_duration=longest_trade_duration,
                           shortest_trade_duration=shortest_trade_duration,
                           prof_weeks_win=prof_weeks_win,
                           prof_weeks_draw=prof_weeks_draw,
                           prof_weeks_loss=prof_weeks_loss,
                           perf_weeks_win=perf_weeks_win,
                           perf_weeks_draw=perf_weeks_draw,
                           perf_weeks_loss=perf_weeks_loss,
                           prof_months_win=prof_months_win,
                           prof_months_draw=prof_months_draw,
                           prof_months_loss=prof_months_loss,
                           perf_months_win=perf_months_win,
                           perf_months_draw=perf_months_draw,
                           perf_months_loss=perf_months_loss,
                           max_seen_drawdown=max_seen_drawdown['drawdown'],
                           drawdown_from=max_seen_drawdown['from'],
                           drawdown_to=max_seen_drawdown['to'],
                           drawdown_at=max_seen_drawdown['at'],
                           longest_realised_drawdown=longest_realised_drawdown,
                           longest_seen_drawdown=longest_seen_drawdown,
                           stoploss=self.config.stoploss,
                           stoploss_type=self.config.stoploss_type,
                           fee=self.config.fee,
                           total_fee_amount=self.trading_module.total_fee_paid,
                           rejected_buy_signal=self.trading_module.rejected_buy_signal,
                           sharpe_90d=sharpe_90d,
                           sharpe_3y=sharpe_3y,
                           sortino_90d=sortino_90d,
                           sortino_3y=sortino_3y,
                           risk_reward_ratio=risk_reward_ratio,
                           volume_turnover=volume_turnover
                           )

    def generate_coin_results(self, closed_trades: [Trade], market_change: dict, market_drawdown: dict,
                              pairs: list) -> [list, dict]:
        stats = self.calculate_statistics_per_coin(closed_trades)
        trade_rankings = compute_trade_rankings(closed_trades, pairs)
        new_stats = []

        for coin in stats:
            avg_profit_ratio = (stats[coin]['cum_profit_ratio'] / stats[coin]['amount_of_trades']) \
                if stats[coin]['amount_of_trades'] > 0 else 0

            coin_insight = CoinInsights(pair=coin,
                                        n_trades=stats[coin]['amount_of_trades'],
                                        n_wins=stats[coin]['amount_of_winning_trades'],
                                        n_losses=stats[coin]['amount_of_losing_trades'],
                                        market_change=market_change[coin],
                                        market_drawdown=market_drawdown[coin],
                                        cum_profit_ratio=stats[coin]['cum_profit_ratio'],
                                        total_profit_ratio=stats[coin]['total_profit_ratio'],
                                        avg_profit_ratio=avg_profit_ratio,
                                        profit=stats[coin]['total_profit_amount'],
                                        max_seen_drawdown=stats[coin]['max_seen_ratio'],
                                        max_realised_drawdown=stats[coin]['max_realised_ratio'],
                                        prof_weeks_win=stats[coin]['prof_weeks_win'],
                                        prof_weeks_draw=stats[coin]['prof_weeks_draw'],
                                        prof_weeks_loss=stats[coin]['prof_weeks_loss'],
                                        perf_weeks_win=stats[coin]['perf_weeks_win'],
                                        perf_weeks_draw=stats[coin]['perf_weeks_draw'],
                                        perf_weeks_loss=stats[coin]['perf_weeks_loss'],
                                        prof_months_win=stats[coin]['prof_months_win'],
                                        prof_months_draw=stats[coin]['prof_months_draw'],
                                        prof_months_loss=stats[coin]['prof_months_loss'],
                                        perf_months_win=stats[coin]['perf_months_win'],
                                        perf_months_draw=stats[coin]['perf_months_draw'],
                                        perf_months_loss=stats[coin]['perf_months_loss'],
                                        avg_trade_duration=stats[coin]['avg_trade_duration'],
                                        longest_trade_duration=stats[coin]['longest_trade_duration'],
                                        shortest_trade_duration=stats[coin]['shortest_trade_duration'],
                                        roi=stats[coin]['sell_reasons'][SellReason.ROI],
                                        stoploss=stats[coin]['sell_reasons'][SellReason.STOPLOSS],
                                        sell_signal=stats[coin]['sell_reasons'][SellReason.SELL_SIGNAL],
                                        best_trade_ratio=trade_rankings[coin]['ratio']['best'] if
                                        trade_rankings[coin]['ratio']['best'] is None else
                                        trade_rankings[coin]['ratio']['best'] - 1,
                                        worst_trade_ratio=trade_rankings[coin]['ratio']['worst'] if
                                        trade_rankings[coin]['ratio']['worst'] is None else
                                        trade_rankings[coin]['ratio']['worst'] - 1,
                                        median_trade_ratio=trade_rankings[coin]['ratio']['median'] if
                                        trade_rankings[coin]['ratio']['median'] is None else
                                        trade_rankings[coin]['ratio']['median'] - 1,
                                        best_trade_currency=trade_rankings[coin]['currency']['best'],
                                        worst_trade_currency=trade_rankings[coin]['currency']['worst'],
                                        median_trade_currency=trade_rankings[coin]['currency']['median'])
            new_stats.append(coin_insight)

        return new_stats

    def calculate_statistics_per_coin(self, closed_trades):
        per_coin_stats = {
            pair: {
                'cum_profit_ratio': 0,
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
                "prof_weeks_win": 0,
                "prof_weeks_draw": 0,
                "prof_weeks_loss": 0,
                "perf_weeks_win": 0,
                "perf_weeks_draw": 0,
                "perf_weeks_loss": 0,
                "prof_months_win": 0,
                "prof_months_draw": 0,
                "prof_months_loss": 0,
                "perf_months_win": 0,
                "perf_months_draw": 0,
                "perf_months_loss": 0
            } for pair in self.frame_with_signals.keys()
        }
        trades_per_coin = group_by(closed_trades, "pair")

        print_info("Calculating statistics")

        if len(trades_per_coin) == 0:
            trades_per_coin = {pair: [] for pair in self.frame_with_signals.keys()}

        for pair, closed_pair_trades in trades_per_coin.items():
            # Calculate max seen drawdown ratio
            seen_cum_profit_ratio_df = get_seen_cum_profit_ratio(
                self.frame_with_signals[pair],
                closed_pair_trades,
                self.config.fee
            )
            per_coin_stats[pair]["max_seen_ratio"] = get_max_drawdown_ratio(seen_cum_profit_ratio_df) - 1

            # Calculate max realised drawdown ratio
            realised_cum_profit_ratio_df = get_realised_profit_ratio(
                self.frame_with_signals[pair],
                closed_pair_trades,
                self.config.fee,
            )
            per_coin_stats[pair]["max_realised_ratio"] = \
                get_max_drawdown_ratio_without_buy_rows(realised_cum_profit_ratio_df)

            # Find avg, longest and shortest trade durations
            per_coin_stats[pair]["avg_trade_duration"], \
            per_coin_stats[pair]["longest_trade_duration"], \
            per_coin_stats[pair]["shortest_trade_duration"] = \
                calculate_trade_durations(closed_pair_trades)

            # Find winning, draw and losing weeks for current coin
            per_coin_stats[pair]["perf_weeks_win"], \
            per_coin_stats[pair]["perf_weeks_draw"], \
            per_coin_stats[pair]["perf_weeks_loss"] = get_outperforming_timeframe(
                seen_cum_profit_ratio_df,
                self.market_ratio_df[pair],
                "W"
            )

            # Find winning, draw and losing months for current coin
            per_coin_stats[pair]["perf_months_win"], \
            per_coin_stats[pair]["perf_months_draw"], \
            per_coin_stats[pair]["perf_months_loss"] = get_outperforming_timeframe(
                seen_cum_profit_ratio_df,
                self.market_ratio_df[pair],
                "M"
            )

            # Find profitable weeks for current coin
            per_coin_stats[pair]["prof_weeks_win"], \
            per_coin_stats[pair]["prof_weeks_draw"], \
            per_coin_stats[pair]["prof_weeks_loss"] = get_profitable_timeframe(
                seen_cum_profit_ratio_df,
                "W"
            )

            # Find profitable months for current coin
            per_coin_stats[pair]["prof_months_win"], \
            per_coin_stats[pair]["prof_months_draw"], \
            per_coin_stats[pair]["prof_months_loss"] = get_profitable_timeframe(
                seen_cum_profit_ratio_df,
                "M"
            )

            for trade in closed_pair_trades:
                # Update average profit
                per_coin_stats[pair]['cum_profit_ratio'] += trade.profit_ratio - 1

                # Update total profit percentage and amount
                per_coin_stats[pair]['total_profit_ratio'] = \
                    per_coin_stats[pair]['total_profit_ratio'] * trade.profit_ratio

                # Update profit and amount of trades
                per_coin_stats[pair]['total_profit_amount'] += trade.profit_currency
                per_coin_stats[pair]['amount_of_trades'] += 1
                if trade.profit_ratio > 1:
                    per_coin_stats[pair]['amount_of_winning_trades'] += 1
                if trade.profit_ratio < 1:
                    per_coin_stats[pair]['amount_of_losing_trades'] += 1
                per_coin_stats[pair]['sell_reasons'][trade.sell_reason] += 1

                # Check for max realised drawdown
                if per_coin_stats[pair]['drawdown_ratio'] < per_coin_stats[pair]['max_realised_ratio']:
                    per_coin_stats[pair]['max_realised_ratio'] = per_coin_stats[pair]['drawdown_ratio']

                # Sum total times
                if per_coin_stats[pair]['total_duration'] is None:
                    per_coin_stats[pair]['total_duration'] = trade.closed_at - trade.opened_at
                else:
                    per_coin_stats[pair]['total_duration'] += trade.closed_at - trade.opened_at

            # Turn into actual ratios
            per_coin_stats[pair]['total_profit_ratio'] -= 1

        return per_coin_stats

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
            ) - 1
            left_open_trade_results = LeftOpenTradeResult(pair=trade.pair,
                                                          curr_profit_ratio=trade.profit_ratio - 1,
                                                          curr_profit=trade.profit_currency,
                                                          max_seen_drawdown=max_seen_drawdown,
                                                          opened_at=trade.opened_at)

            left_open_trade_stats.append(left_open_trade_results)
        return left_open_trade_stats
