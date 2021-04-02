# Libraries
from dataclasses import dataclass
from datetime import datetime
from tabulate import tabulate
import typing

FONT_BOLD = "\033[1m"
FONT_RESET = "\033[0m"


def show_signature():
    print("======================================================================")
    print("%s|  DEMA BACKTESTING ENGINE IS SUBJECTED TO THE GNU AGPL-3.0 License %s" %
          (FONT_BOLD, FONT_RESET))
    print("%s|  Copyright © 2021 - DemaTrading.ai%s" %
          (FONT_BOLD, FONT_RESET))
    print("======================================================================")


@dataclass
class MainResults:
    tested_from: datetime
    tested_to: datetime
    starting_capital: float
    end_capital: float
    overall_profit_percentage: float
    n_trades: int
    n_left_open_trades: int
    n_trades_with_loss: int
    max_realized_drawdown: float
    max_drawdown_single_trade: float
    max_seen_drawdown: float
    drawdown_from: datetime
    drawdown_to: datetime
    configured_stoploss: float
    total_fee_amount: float

    def show(self, currency_symbol: str):
        print("================================================= \n| %sBacktesting Results%s "
              "\n=================================================" % (FONT_BOLD, FONT_RESET))
        print("| Backtesting from: \t\t%s" % self.tested_from)
        print("| Backtesting to: \t\t%s" % self.tested_to)
        print("| ")
        print("| Started with: \t\t%s" %
              round(self.starting_capital, 2) + '\t' + currency_symbol)
        print("| Ended with: \t\t\t%s" %
              round(self.end_capital, 2) + '\t' + currency_symbol)
        print("| Overall profit: \t\t%s" %
              round(self.overall_profit_percentage, 2) + '\t%')
        print("| Amount of trades: \t\t%s" % self.n_trades)
        print("| Left-open trades: \t\t%s" % self.n_left_open_trades)
        print("| Trades with loss: \t\t%s" % self.n_trades_with_loss)
        print("| Stoploss: \t\t\t%s" % self.configured_stoploss + "\t%")
        print("| ")
        print("| Max realized drawdown:\t%s" %
              round(self.max_realized_drawdown, 2) + '\t%')
        print("| Max drawdown 1 trade: \t%s" %
              round(self.max_drawdown_single_trade, 2) + '\t%')
        print("| Max seen drawdown: \t\t%s" %
              round(self.max_seen_drawdown, 2) + '\t%')
        print("| Seen drawdown from: \t\t%s" % self.drawdown_from)
        print("| Seen drawdown to: \t\t%s" % self.drawdown_to)
        print("| Total fee paid: \t\t%s" % self.total_fee_amount)


@dataclass
class CoinInsights:
    pair: str
    avg_profit_percentage: float
    profit: float
    n_trades: int
    max_drawdown: float
    avg_duration: datetime
    roi: int
    stoploss: int
    sell_signal: int

    @staticmethod
    def show(instances: typing.List['CoinInsights'], currency_symbol: str):
        print("================================================="
              "\n| %s Per coin insights %s " % (FONT_BOLD, FONT_RESET))

        stats = []
        for c in instances:
            stats.append([c.pair, round(c.avg_profit_percentage, 2), round(c.profit, 2),
                          c.n_trades, round(c.max_drawdown, 2),
                          c.avg_duration, c.roi, c.stoploss,
                          c.sell_signal])

        print(tabulate(stats,
                       headers=['Pair',
                                'avg profit (%)',
                                f' profit ({currency_symbol})',
                                'trades',
                                'max drawdown %',
                                'avg duration',
                                'ROI', 'SL', 'Signal'],
                       tablefmt='pretty'))


@dataclass
class OpenTradeResult:
    pair: str
    curr_profit_percentage: float
    curr_profit: float
    max_drawdown: float
    opened_at: datetime

    @staticmethod
    def show(instances: typing.List['OpenTradeResult'], currency_symbol):
        print("| %sLeft open trades %s" % (FONT_BOLD, FONT_RESET))
        rows = []
        for res in instances:
            rows.append([res.pair,
                         round(res.curr_profit_percentage, 2),
                         round(res.curr_profit, 2),
                         round(res.max_drawdown, 2),
                         res.opened_at])
        print(tabulate(rows,
                       headers=['Pair', 'cur. profit (%)',
                                f' cur. profit ({currency_symbol})',
                                'max drawdown %', 'opened at'],
                       tablefmt='pretty'))
