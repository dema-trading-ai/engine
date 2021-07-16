import json
import os

from cli.print_utils import print_warning, print_error, print_info
from modules.output.plots_per_coin import plot_per_coin
from modules.output.results import show_signature, CoinInsights, LeftOpenTradeResult, show_mainresults
from modules.public.trading_stats import TradingStats
from modules.stats.stats_config import StatsConfig
from modules.stats.trade import SellReason

FONT_BOLD = "\033[1m"
FONT_RESET = "\033[0m"


class OutputModule(object):
    config: StatsConfig

    def __init__(self, config: StatsConfig):
        self.config = config

    def output(self, stats: TradingStats):
        # print tables
        show_mainresults(stats.main_results, self.config.currency_symbol)
        CoinInsights.show(stats.coin_results, self.config.currency_symbol)
        LeftOpenTradeResult.show(stats.open_trade_results, self.config.currency_symbol)

        show_trade_anomalies(stats)

        # check for correct window width
        try:
            terminal_width = os.get_terminal_size().columns
            if terminal_width < 108:  # minimal terminal width
                print_error("Your terminal width is too small. Increase "
                            "terminal width to display results correctly.")
        except OSError:
            pass

        print_info("Logging trades to " + FONT_BOLD + "data/backtesting-data/trades_log.json" + FONT_RESET + "...")
        log_trades(stats)

        # plot graphs
        if self.config.plots:
            print_info("Creating plots in " + FONT_BOLD + "data/backtesting-data/plots" + FONT_RESET + "...")
            plot_per_coin(stats, config=self.config)
        print_info("Backtest finished!")

        show_signature()


def show_trade_anomalies(stats: TradingStats):
    trades = list(filter(lambda x: x.sell_reason == SellReason.STOPLOSS_AND_ROI, stats.trades))

    if len(trades) > 0:
        print_warning("Both Stoploss and ROI were triggered in the same candle, during the "
                      "following trade(s):")
        for trade in trades:
            print_warning(f"- {trade.opened_at} ==> {trade.closed_at}")
        print_warning("Profit for affected trades will be set to 0%")


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
