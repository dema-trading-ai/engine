# Libraries
from dataclasses import dataclass
from datetime import datetime
from tabulate import tabulate
import typing

# Files
from utils.utils import CURRENT_VERSION

FONT_BOLD = "\033[1m"
FONT_RESET = "\033[0m"


def show_signature():
    print("======================================================================")
    print("%s|  DemaTrading.ai BACKTESTING ENGINE IS SUBJECTED TO THE GNU AGPL-3.0 License %s" %
          (FONT_BOLD, FONT_RESET))
    print("%s|  Copyright © 2021 - DemaTrading.ai%s" %
          (FONT_BOLD, FONT_RESET))
    print("======================================================================")


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
    best_trade_profit_percentage: float
    max_seen_drawdown: float
    drawdown_from: datetime
    drawdown_to: datetime
    drawdown_at: datetime
    configured_stoploss: float
    fee: float
    total_fee_amount: float

    def show(self, currency_symbol: str):
        print("================================================= \n| %sBacktesting Results%s "
              "\n=================================================" % (FONT_BOLD, FONT_RESET))
        print("| Engine version \t\t%s" % CURRENT_VERSION)
        print("| ")
        print("| Backtesting from: \t\t%s" % self.tested_from)
        print("| Backtesting to: \t\t%s" % self.tested_to)
        print("| Max open trades: \t\t%s" % self.max_open_trades)
        print("| Stoploss: \t\t\t%s" % self.configured_stoploss + "\t%")
        print("| ")
        print("| Started with: \t\t%s" %
              round(self.starting_capital, 2) + '\t' + currency_symbol)
        print("| Ended with: \t\t\t%s" %
              round(self.end_capital, 2) + '\t' + currency_symbol)
        print("| Overall profit: \t\t%s" %
              round(self.overall_profit_percentage, 2) + '\t%')
        print("| Amount of trades: \t\t%s" % self.n_trades)
        print("| Average trades per day: \t%s" % round(self.n_average_trades, 2))
        print("| Left-open trades: \t\t%s" % self.n_left_open_trades)
        print("| Trades with loss: \t\t%s" % self.n_trades_with_loss)
        print("| Most consecutive losses: \t%s" % self.n_consecutive_losses)
        print("| ")
        print("| Best trade: \t\t\t%s" %
              round(self.best_trade_profit_percentage, 2) + '\t%')
        print("| Worst trade: \t\t\t%s" %
              round(self.worst_trade_profit_percentage, 2) + '\t%')
        print("| Max realised drawdown:\t%s" %
              round(self.max_realised_drawdown, 2) + '\t%')
        print("| Max seen drawdown: \t\t%s" %
              round(self.max_seen_drawdown, 2) + '\t%')
        print("| Max seen drawdown from: \t%s" % self.drawdown_from)
        print("| Max seen drawdown to: \t%s" % self.drawdown_to)
        print("| Max seen drawdown at: \t%s" % self.drawdown_at)
        print("| Market change coins: \t\t%s" % round(self.market_change_coins, 2) + '\t%')
        print("| Market change BTC: \t\t%s" % round(self.market_change_btc, 2) + '\t%')
        print("| ")
        print("| Fee percentage: \t\t%s" % self.fee + '\t%')
        print("| Total fee paid: \t\t%s" % round(self.total_fee_amount, 2) + "\t" + currency_symbol)


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
        print("================================================="
              "\n| %s Per coin insights %s " % (FONT_BOLD, FONT_RESET))

        stats = []
        for c in instances:
            stats.append([c.pair,
                        c.n_trades,
                        round(c.market_change, 2),
                        round(c.avg_profit_percentage, 2),
                        round(c.cum_profit_percentage, 2),
                        round(c.total_profit_percentage, 2),
                        round(c.profit, 2)])

        print(tabulate(stats,
                       headers=['Pair',
                                'trades',
                                'market change (%)',
                                'avg profit (%)',
                                'cum profit (%)',
                                'total profit (%)',
                                f' profit ({currency_symbol})'],
                       tablefmt='pretty'))

        stats = []
        for c in instances:
            stats.append([c.pair,
                        round(c.max_seen_drawdown, 2),
                        round(c.max_realised_drawdown, 2),
                        c.avg_trade_duration,
                        c.roi,
                        c.stoploss,
                        c.sell_signal])

        print(tabulate(stats,
                       headers=['Pair',
                                'max seen drawdown %',
                                'max realised drawdown %',
                                'avg trade duration',
                                'ROI',
                                'SL',
                                'Signal'],
                       tablefmt='pretty'))


@dataclass
class OpenTradeResult:
    pair: str
    curr_profit_percentage: float
    curr_profit: float
    max_seen_drawdown: float
    opened_at: datetime

    @staticmethod
    def show(instances: typing.List['OpenTradeResult'], currency_symbol):
        print("| %sLeft open trades %s" % (FONT_BOLD, FONT_RESET))
        rows = []
        for res in instances:
            rows.append([res.pair,
                         round(res.curr_profit_percentage, 2),
                         round(res.curr_profit, 2),
                         round(res.max_seen_drawdown, 2),
                         res.opened_at])
        print(tabulate(rows,
                       headers=['Pair',
                                'cur. profit (%)',
                                f' cur. profit ({currency_symbol})',
                                'max seen drawdown',
                                'opened at'],
                       tablefmt='pretty'))
