# Libraries
import math
from dataclasses import dataclass
from datetime import datetime, timedelta
import typing

from rich.console import JustifyMethod
from rich.padding import Padding
from rich.table import Table
from rich import box

# Files
from cli.print_utils import print_standard, console_color
from modules.public.trading_stats import MainResults
from utils.utils import CURRENT_VERSION


def show_signature():
    print_standard(
        "================================================================================\n"
        "   DemaTrading.ai BACKTESTING ENGINE IS SUBJECTED TO THE GNU AGPL-3.0 License\n"
        "   Copyright © 2021 - DemaTrading.ai\n"
        "================================================================================")


def colorize(value, condition, symbol=""):
    if value > condition:
        return f"[bright_green]{value}[/bright_green] {symbol}"
    elif value < condition:
        return f"[bright_red]{value}[/bright_red] {symbol}"
    else:
        return f"[orange1]{value}[/orange1] {symbol}"


def timestamp_to_string(time_stamp: int) -> str:
    return datetime.fromtimestamp(time_stamp / 1000).strftime('%Y-%m-%d ''%H:%M') \
        if time_stamp != 0 else '-'


def format_time_difference(avg_trade_duration_unformatted: timedelta) -> str:
    if avg_trade_duration_unformatted != timedelta(0):
        avg_trade_duration_rounded = timedelta(seconds=round(avg_trade_duration_unformatted.total_seconds()))
        avg_trade_duration = str(avg_trade_duration_rounded)
    else:
        avg_trade_duration = '-'
    return avg_trade_duration


def show_mainresults(self: MainResults, currency_symbol: str):
    # Update variables for prettier terminal output
    drawdown_from_string = timestamp_to_string(self.drawdown_from)
    drawdown_to_string = timestamp_to_string(self.drawdown_to)
    drawdown_at_string = timestamp_to_string(self.drawdown_at)

    tested_from_string = self.tested_from.strftime('%Y-%m-%d ''%H:%M')
    tested_to_string = self.tested_to.strftime('%Y-%m-%d ''%H:%M')

    justification: JustifyMethod = "left"

    # Settings table
    settings_table = create_settings_table(self,
                                           currency_symbol,
                                           justification,
                                           tested_from_string,
                                           tested_to_string
                                           )

    # Performance table
    performance_table = create_performance_table(self,
                                                 currency_symbol,
                                                 drawdown_at_string,
                                                 drawdown_from_string,
                                                 drawdown_to_string,
                                                 justification
                                                 )

    # Trade info table
    trade_info_table = create_trade_info_table(self, justification)

    # Create grid for all tables
    table_grid = Table(box=box.SIMPLE)
    table_grid.add_column(f":robot: {self.strategy_name}'s Backtest brought to you by DemaTrading.ai's Engine :robot:")
    tables = Table.grid()
    tables.add_row(settings_table)
    tables.add_row(performance_table, Padding(trade_info_table, (0, 2)))
    table_grid.add_row(tables)
    console_color.print(table_grid)


def create_trade_info_table(self, justification) -> Table:
    avg_trade_duration = format_time_difference(self.avg_trade_duration)
    longest_trade_duration = format_time_difference(self.longest_trade_duration)
    shortest_trade_duration = format_time_difference(self.shortest_trade_duration)

    trade_info_table = Table(box=box.ROUNDED)
    trade_info_table.add_column("Trade Info "
                                ":mag:",
                                justify=justification,
                                style="white")
    trade_info_table.add_column(justify=justification)
    trade_info_table.add_row('Amount of trades', str(self.n_trades))
    trade_info_table.add_row('Avg. trades per day',
                             str(round(self.n_average_trades, 2)))
    trade_info_table.add_row('Left-open trades', str(self.n_left_open_trades))
    trade_info_table.add_row('Trades with loss', str(self.n_trades_with_loss))
    trade_info_table.add_row('Rejected buy signals', str(self.rejected_buy_signal))
    trade_info_table.add_row('Most consecutive losses',
                             str(self.n_consecutive_losses))
    trade_info_table.add_row(f'Best trade',
                             colorize(round(
                                 self.best_trade_profit_percentage, 2),
                                 0, f'% ({self.best_trade_pair})'))
    trade_info_table.add_row(f'Worst trade',
                             colorize(round(
                                 self.worst_trade_profit_percentage, 2),
                                 0, f'% ({self.worst_trade_pair})'))
    trade_info_table.add_row('Shortest trade duration', str(shortest_trade_duration))
    trade_info_table.add_row('Avg. trade duration', str(avg_trade_duration))
    trade_info_table.add_row('Longest trade duration', str(longest_trade_duration))
    trade_info_table.add_row('Profitable weeks (W/D/L)', f'{self.prof_weeks_win} / {self.prof_weeks_draw}'
                                                      f' / {self.prof_weeks_loss}')
    trade_info_table.add_row('Weekly perf. vs market (W/D/L)', f'{self.win_weeks} / {self.draw_weeks}'
                                                      f' / {self.loss_weeks}')
    return trade_info_table


def create_performance_table(self, currency_symbol, drawdown_at_string, drawdown_from_string, drawdown_to_string,
                             justification) -> Table:
    performance_table = Table(box=box.ROUNDED)
    performance_table.add_column("Performance "
                                 ":chart_with_upwards_trend:", justify=justification,
                                 style="white", width=25)
    performance_table.add_column(justify=justification, width=20)
    performance_table.add_row('End capital',
                              colorize(round(self.end_capital, 2),
                                       round(self.starting_capital, 2),
                                       str(currency_symbol)))
    performance_table.add_row('Overall profit',
                              colorize(round(
                                  self.overall_profit_percentage, 2), 0, '%'))
    performance_table.add_row('Max. realised drawdown',
                              colorize(round(self.max_realised_drawdown,
                                             2), 0, '%'))
    performance_table.add_row('Max. seen drawdown',
                              colorize(round(self.max_seen_drawdown,
                                             2), 0, '%'))
    performance_table.add_row('Max. seen drawdown from',
                              drawdown_from_string)
    performance_table.add_row('Max. seen drawdown to', drawdown_to_string)
    performance_table.add_row('Max. seen drawdown at', drawdown_at_string)
    performance_table.add_row('Market change coins',
                              colorize(round(self.market_change_coins,
                                             2), 0, '%'))
    performance_table.add_row('Market change BTC/USDT',
                              colorize(round(self.market_change_btc,
                                             2), 0, '%'))
    performance_table.add_row('Market drawdown coins',
                              colorize(round(self.market_drawdown_coins,
                                             2), 0, '%'))
    performance_table.add_row('Market drawdown BTC/USDT',
                              colorize(round(self.market_drawdown_btc,
                                             2), 0, '%'))
    performance_table.add_row('Sharpe ratio (90d / 3y)', str(round(self.ratios[0], 2)) + ' / ' + str(round(self.ratios[1], 2)) if not (math.isnan(self.ratios[0]) or math.isinf(self.ratios[0])) else '- / -')
    performance_table.add_row('Sortino ratio (90d / 3y)', str(round(self.ratios[2], 2)) + ' / ' + str(round(self.ratios[3], 2)) if not (math.isnan(self.ratios[2]) or math.isinf(self.ratios[2])) else '- / -')
    performance_table.add_row('Total fee paid',
                              f"{round(self.total_fee_amount)} {currency_symbol}")
    return performance_table


def create_settings_table(self: MainResults, currency_symbol, justification, tested_from_string,
                          tested_to_string) -> Table:
    settings_table = Table(box=box.ROUNDED)
    settings_table.add_column("Settings "
                              ":wrench:",
                              justify=justification,
                              width=25)
    settings_table.add_column(justify=justification, width=20)
    settings_table.add_row("Engine version", CURRENT_VERSION)
    settings_table.add_row("Strategy", self.strategy_name)
    settings_table.add_row("Backtesting from", tested_from_string)
    settings_table.add_row("Backtesting to", tested_to_string)
    settings_table.add_row("Timeframe", self.timeframe)
    stoploss_setting = f"{self.stoploss} % ({self.stoploss_type})" if \
        self.stoploss_type != 'dynamic' else self.stoploss_type
    settings_table.add_row("Stoploss", stoploss_setting)
    settings_table.add_row("Start capital",
                           f"{round(self.starting_capital, 2)} {currency_symbol}")
    settings_table.add_row("Fee percentage", f"{self.fee} %")
    settings_table.add_row("Max. open trades", str(self.max_open_trades))
    settings_table.add_row("Exposure per trade", str(round(self.exposure_per_trade * 100, 2)) + " %")
    return settings_table


@dataclass
class CoinInsights:
    pair: str
    cum_profit_percentage: float
    total_profit_percentage: float
    avg_profit_percentage: float
    profit: float
    n_trades: int
    n_wins: int
    n_losses: int
    market_change: float
    market_drawdown: float
    max_seen_drawdown: float
    max_realised_drawdown: float
    prof_weeks_win: int
    prof_weeks_draw: int
    prof_weeks_loss: int
    win_weeks: int
    draw_weeks: int
    loss_weeks: int
    avg_trade_duration: timedelta
    longest_trade_duration: timedelta
    shortest_trade_duration: timedelta
    roi: int
    stoploss: int
    sell_signal: int

    @staticmethod
    def show(instances: typing.List['CoinInsights'], currency_symbol: str):
        justification: JustifyMethod = "center"

        coin_performance_table = CoinInsights.create_coin_performance_table(justification, currency_symbol)

        coin_metrics_table = CoinInsights.create_coin_metrics_table(justification)

        coin_signal_table = CoinInsights.create_coin_signals_table(justification)

        for c in instances:
            avg_trade_duration = format_time_difference(c.avg_trade_duration)
            longest_trade_duration = c.longest_trade_duration if c.longest_trade_duration != timedelta(0) else '-'
            shortest_trade_duration = c.shortest_trade_duration if c.shortest_trade_duration != timedelta(0) else '-'

            coin_performance_table.add_row(c.pair,
                                           colorize(round(c.avg_profit_percentage, 2), 0),
                                           colorize(round(c.cum_profit_percentage, 2), 0),
                                           colorize(round(c.total_profit_percentage, 2), 0),
                                           colorize(round(c.profit, 2), 0),
                                           )

            coin_metrics_table.add_row(c.pair,
                                       colorize(round(c.market_change, 2), 0),
                                       colorize(round(c.market_drawdown, 2), 0),
                                       colorize(round(c.max_seen_drawdown, 2), 0),
                                       colorize(round(c.max_realised_drawdown, 2), 0),
                                       f"{c.win_weeks} / {c.draw_weeks} / {c.loss_weeks}",
                                       f"{c.prof_weeks_win} / {c.prof_weeks_draw} / {c.prof_weeks_loss}",
                                       )

            coin_signal_table.add_row(c.pair,
                                      f"{c.n_trades} ([bright_green]{c.n_wins}[/bright_green]/[bright_red]{c.n_losses}[/bright_red])",
                                      str(shortest_trade_duration),
                                      str(avg_trade_duration),
                                      str(longest_trade_duration),
                                      str(c.roi),
                                      str(c.stoploss),
                                      str(c.sell_signal),
                                      )
        # Create grid for all tables
        table_grid = Table(box=box.SIMPLE)
        table_grid.add_column(":moneybag: COIN INSIGHTS :moneybag:")
        table_grid.add_row(coin_performance_table)
        table_grid.add_row(coin_metrics_table)
        table_grid.add_row(coin_signal_table)
        console_color.print(table_grid)

    @staticmethod
    def create_coin_signals_table(justification) -> Table:
        coin_signal_table = Table(title="Coin Signals", box=box.ROUNDED, width=100)
        coin_signal_table.add_column("Pair", justify=justification)
        coin_signal_table.add_column("Trades (W/L)", justify=justification)
        coin_signal_table.add_column("Shortest trade duration", justify=justification)
        coin_signal_table.add_column("Avg. trade duration", justify=justification)
        coin_signal_table.add_column("Longest trade duration", justify=justification)
        coin_signal_table.add_column("ROI", justify=justification)
        coin_signal_table.add_column("SL", justify=justification)
        coin_signal_table.add_column("Signal", justify=justification)
        return coin_signal_table

    @staticmethod
    def create_coin_metrics_table(justification) -> Table:
        coin_metrics_table = Table(title="Coin Metrics", box=box.ROUNDED, width=100)
        coin_metrics_table.add_column("Pair", justify=justification)
        coin_metrics_table.add_column("Market change (%)", justify=justification)
        coin_metrics_table.add_column("Market drawdown (%)", justify=justification)
        coin_metrics_table.add_column("Max. seen drawdown (%)", justify=justification)
        coin_metrics_table.add_column("Max. realised drawdown (%)",
                                      justify=justification)
        coin_metrics_table.add_column("Weekly perf. vs market (W/D/L)",
                                      justify=justification)
        coin_metrics_table.add_column("Profitable weeks (W/D/L)",
                                      justify=justification)
        return coin_metrics_table

    @staticmethod
    def create_coin_performance_table(justification, currency_symbol: str) -> Table:
        coin_performance_table = Table(title="Coin Performance",
                                       box=box.ROUNDED,
                                       width=100)
        coin_performance_table.add_column("Pair", justify=justification)
        coin_performance_table.add_column("Avg. profit (%)", justify=justification)
        coin_performance_table.add_column("Cum. profit (%)", justify=justification)
        coin_performance_table.add_column("Total profit (%)", justify=justification)
        coin_performance_table.add_column(f"Profit ({currency_symbol})", justify=justification)
        return coin_performance_table


@dataclass
class LeftOpenTradeResult:
    pair: str
    curr_profit_percentage: float
    curr_profit: float
    max_seen_drawdown: float
    opened_at: datetime

    @staticmethod
    def show(instances: typing.List['LeftOpenTradeResult'], currency_symbol):
        justification: JustifyMethod = "center"

        left_open_trades_table = LeftOpenTradeResult.create_left_open_trades_table(justification, currency_symbol)

        for c in instances:
            left_open_trades_table.add_row(c.pair,
                                           colorize(round(c.curr_profit_percentage, 2), 0),
                                           colorize(round(c.curr_profit, 2), 0),
                                           colorize(round(c.max_seen_drawdown, 2), 0),
                                           str(c.opened_at),
                                           )

        table_grid = Table(box=box.SIMPLE)
        table_grid.add_column(":hourglass_flowing_sand: LEFT OPEN TRADES :hourglass_flowing_sand:")
        table_grid.add_row(left_open_trades_table)
        console_color.print(table_grid)

    @staticmethod
    def create_left_open_trades_table(justification, currency_symbol) -> Table:
        left_open_trades_table = Table(title="Left open trades", box=box.ROUNDED, width=100)
        left_open_trades_table.add_column("Pair", justify=justification)
        left_open_trades_table.add_column("Cur. profit (%)", justify=justification)
        left_open_trades_table.add_column(f"Cur. profit ({currency_symbol})", justify=justification)
        left_open_trades_table.add_column("Max. seen drawdown (%)", justify=justification)
        left_open_trades_table.add_column("Opened at", justify=justification)
        return left_open_trades_table
