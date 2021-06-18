# Libraries
from dataclasses import dataclass
from datetime import datetime
import typing
from rich.console import Console, JustifyMethod
from rich.table import Table
from rich import box

# Files
from utils import CURRENT_VERSION

FONT_BOLD = "\033[1m"
FONT_RESET = "\033[0m"

console = Console()


def show_signature():
    print("================================================================================")
    print("%s   DemaTrading.ai BACKTESTING ENGINE IS SUBJECTED TO THE GNU AGPL-3.0 License %s" %
          (FONT_BOLD, FONT_RESET))
    print("%s   Copyright © 2021 - DemaTrading.ai%s" %
          (FONT_BOLD, FONT_RESET))
    print("================================================================================")


def colorize(value, condition, symbol=""):
    if value > condition:
        return f"[bright_green]{value}[/bright_green] {symbol}"
    elif value < condition:
        return f"[bright_red]{value}[/bright_red] {symbol}"
    else:
        return f"[orange1]{value}[/orange1] {symbol}"


@dataclass
class MainResults:
    tested_from: datetime
    tested_to: datetime
    max_open_trades: int
    market_change_coins: float
    market_change_btc: float
    starting_capital: float
    end_capital: float
    overall_profit_percentage: float
    n_trades: int
    n_average_trades: float
    n_left_open_trades: int
    n_trades_with_loss: int
    n_consecutive_losses: int
    max_realised_drawdown: float
    worst_trade_profit_percentage: float
    worst_trade_pair: str
    best_trade_profit_percentage: float
    best_trade_pair: str
    max_seen_drawdown: float
    drawdown_from: datetime
    drawdown_to: datetime
    drawdown_at: datetime
    stoploss: float
    stoploss_type: str
    fee: float
    total_fee_amount: float

    def show(self, currency_symbol: str):
        justification: JustifyMethod = "left"

        # Settings table
        settings_table = Table(box=box.ROUNDED)
        settings_table.add_column("Settings "
                                  ":wrench:",
                                  justify=justification,
                                  width=25)
        settings_table.add_column(justify=justification, width=20)
        settings_table.add_row("Engine version", CURRENT_VERSION)
        settings_table.add_row("Backtesting from", str(self.tested_from))
        settings_table.add_row("Backtesting to", str(self.tested_to))
        stoploss_setting = f"{self.stoploss} % ({self.stoploss_type})" if \
            self.stoploss_type != 'dynamic' else self.stoploss_type
        settings_table.add_row("Stoploss", stoploss_setting)
        settings_table.add_row("Start capital",
                               f"{round(self.starting_capital, 2)} {currency_symbol}")
        settings_table.add_row("Fee percentage", f"{self.fee} %")
        settings_table.add_row("Max open trades", str(self.max_open_trades))

        # Performance table
        performance_table = Table(box=box.ROUNDED)
        performance_table.add_column("Performance "
                                     ":chart_with_upwards_trend:", justify=justification,
                                     style="cyan", width=25)
        performance_table.add_column(justify=justification, width=20)
        performance_table.add_row('End capital',
                                  colorize(round(self.end_capital, 2),
                                           round(self.starting_capital, 2),
                                           str(currency_symbol)))
        performance_table.add_row('Overall profit',
                                  colorize(round(
                                      self.overall_profit_percentage, 2), 0, '%'))
        performance_table.add_row('Max realised drawdown',
                                  colorize(round(self.max_realised_drawdown,
                                                 2), 0, '%'))
        performance_table.add_row('Max seen drawdown',
                                  colorize(round(self.max_seen_drawdown,
                                                 2), 0, '%'))
        performance_table.add_row('Max seen drawdown from',
                                  str(self.drawdown_from))
        performance_table.add_row('Max seen drawdown to', str(self.drawdown_to))
        performance_table.add_row('Max seen drawdown at', str(self.drawdown_at))
        performance_table.add_row('Market change coins',
                                  colorize(round(self.market_change_coins,
                                                 2), 0, '%'))
        performance_table.add_row('Market change BTC',
                                  colorize(round(self.market_change_btc,
                                                 2), 0, '%'))
        performance_table.add_row('Total fee paid',
                                  f"{round(self.total_fee_amount)} {currency_symbol}")

        # Trade info table
        trade_info_table = Table(box=box.ROUNDED)
        trade_info_table.add_column("Trade Info "
                                    ":mag:",
                                    justify=justification,
                                    style="magenta")
        trade_info_table.add_column(justify=justification)
        trade_info_table.add_row('Amount of trades', str(self.n_trades))
        trade_info_table.add_row('Average trades per day',
                                 str(round(self.n_average_trades, 2)))
        trade_info_table.add_row('Left-open trades', str(self.n_left_open_trades))
        trade_info_table.add_row('Trades with loss', str(self.n_trades_with_loss))
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

        # Create grid for all tables
        table_grid = Table(box=box.SIMPLE)
        table_grid.add_column(":robot: BACKTESTING RESULTS :robot:")
        table_grid.add_row(settings_table)
        table_grid.add_row(performance_table, trade_info_table)
        console.print(table_grid)


@dataclass
class CoinInsights:
    pair: str
    cum_profit_percentage: float
    total_profit_percentage: float
    avg_profit_percentage: float
    profit: float
    n_trades: int
    market_change: float
    max_seen_drawdown: float
    max_realised_drawdown: float
    avg_trade_duration: datetime
    roi: int
    stoploss: int
    sell_signal: int

    @staticmethod
    def show(instances: typing.List['CoinInsights'], currency_symbol: str):
        justification: JustifyMethod = "center"

        coin_performance_table = Table(title="Coin performance",
                                       box=box.ROUNDED)
        coin_performance_table.add_column("Pair", justify=justification)
        coin_performance_table.add_column("Avg. profit (%)", justify=justification, width=15)
        coin_performance_table.add_column("Cum. profit (%)", justify=justification, width=15)
        coin_performance_table.add_column("Total profit (%)", justify=justification, width=20)
        coin_performance_table.add_column("Profit (%)", justify=justification, width=12)

        coin_metrics_table = Table(title="Coin Metrics", box=box.ROUNDED)
        coin_metrics_table.add_column("Pair", justify=justification)
        coin_metrics_table.add_column("Market change (%)", justify=justification)
        coin_metrics_table.add_column("Max. seen drawdown (%)", justify=justification)
        coin_metrics_table.add_column("Max. realised drawdown (%)",
                                      justify=justification)

        coin_signal_table = Table(title="Coin Signals", box=box.ROUNDED)
        coin_signal_table.add_column("Pair", justify=justification)
        coin_signal_table.add_column("Trades", justify=justification, width=10)
        coin_signal_table.add_column("Avg. trade duration",
                                      justify=justification, width=25)
        coin_signal_table.add_column("ROI", justify=justification, width=8)
        coin_signal_table.add_column("SL", justify=justification, width=8)
        coin_signal_table.add_column("Signal", justify=justification, width=8)

        for c in instances:
            coin_performance_table.add_row(c.pair,
                                           colorize(round(c.avg_profit_percentage, 2), 0),
                                           colorize(round(c.cum_profit_percentage, 2), 0),
                                           colorize(round(c.total_profit_percentage, 2), 0),
                                           colorize(round(c.profit, 2), 0),
                                           )

            coin_metrics_table.add_row(c.pair,
                                       colorize(round(c.market_change, 2), 0),
                                       colorize(round(c.max_seen_drawdown, 2), 0),
                                       colorize(round(c.max_realised_drawdown, 2), 0),
                                       )

            coin_signal_table.add_row(c.pair,
                                      str(c.n_trades),
                                      str(c.avg_trade_duration),
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
        console.print(table_grid)


@dataclass
class OpenTradeResult:
    pair: str
    curr_profit_percentage: float
    curr_profit: float
    max_seen_drawdown: float
    opened_at: datetime

    @staticmethod
    def show(instances: typing.List['OpenTradeResult'], currency_symbol):
        justification: JustifyMethod = "center"

        open_trades_table = Table(title="Left open trades", box=box.ROUNDED)
        open_trades_table.add_column("Pair", justify=justification)
        open_trades_table.add_column("Cur. profit (%)", justify=justification, width=15)
        open_trades_table.add_column(f"Cur. profit ({currency_symbol})", justify=justification, width=15)
        open_trades_table.add_column("Max. seen drawdown (%)", justify=justification, width=25)
        open_trades_table.add_column("Opened at", justify=justification, width=25)

        for c in instances:
            open_trades_table.add_row(c.pair,
                                      colorize(round(c.curr_profit_percentage, 2), 0),
                                      colorize(round(c.curr_profit, 2), 0),
                                      colorize(round(c.max_seen_drawdown, 2), 0),
                                      str(c.opened_at),
                                      )

        table_grid = Table(box=box.SIMPLE)
        table_grid.add_column(":hourglass_flowing_sand:  LEFT OPEN TRADES :hourglass_flowing_sand:")
        table_grid.add_row(open_trades_table)
        console.print(table_grid)
