import json
import os

from cli.print_utils import print_warning
from modules.output.plots import plot_per_coin
from modules.output.results import show_signature, CoinInsights, LeftOpenTradeResult
from modules.stats.stats_config import StatsConfig
from modules.stats.trade import SellReason
from modules.stats.trading_stats import TradingStats
from rich.console import Console

console = Console(color_system="truecolor", width=110)


class OutputModule(object):
    config: StatsConfig

    def __init__(self, config: StatsConfig):
        self.config = config

    def output(self, stats: TradingStats):
        # print tables
        stats.main_results.show(self.config.currency_symbol)
        CoinInsights.show(stats.coin_results, self.config.currency_symbol)
        LeftOpenTradeResult.show(stats.open_trade_results, self.config.currency_symbol)

        show_trade_anomalies(stats)

        # check for correct window width
        try:
            terminal_width = os.get_terminal_size().columns
            if terminal_width < 108:  # minimal terminal width
                console.print("[bright_yellow][ERROR] Your terminal width is too small. Increase "
                              "terminal width to display results correctly. [/bright_yellow]")
        except OSError:
            console.print("[bright_yellow][WARNING] Please run in a standard terminal to display "
                          "results correctly. [/bright_yellow]")

        show_signature()

        log_trades(stats)

        # plot graphs
        if self.config.plots:
            plot_per_coin(stats, config=self.config)


def show_trade_anomalies(stats: TradingStats):
    trades = list(filter(lambda x: x.sell_reason == SellReason.STOPLOSS_AND_ROI, stats.trades))

    if len(trades) > 0:
        print_warning("WARNING: Both Stoploss and ROI were triggered in the same candle")
        print_warning("during the following trade(s):")
        for trade in trades:
            print_warning(f"- {trade.opened_at} ==> {trade.closed_at}")
        print_warning("profit for affected trades will be set to 0%")


def log_trades(stats: TradingStats):
    trades_dict = {}
    for trade in stats.trades:
        trade_dict = {'status': trade.status,
                      'opened_at': trade.opened_at,
                      'closed_at': trade.closed_at,
                      'pair': trade.pair,
                      'open_price': trade.open,
                      'fee_paid': trade.fee,
                      'starting_amount': trade.starting_amount,
                      'capital': trade.capital,
                      'currency_amount': trade.currency_amount,
                      'sell_reason': trade.sell_reason}
        trades_dict[str(trade.opened_at)] = trade_dict

    trades_dict = dict(sorted(trades_dict.items()))

    trades_json = json.dumps(trades_dict, indent=4, default=str)

    with open('./data/backtesting-data/trades_log.json', 'w', encoding='utf-8') as f:
        f.write(trades_json)
