from enum import Enum

from backtesting.results import show_signature
from models.trade import SellReason
from modules.stats.stats_config import StatsConfig
from modules.stats.trading_stats import TradingStats


class OutputModule(object):
    config: StatsConfig

    def __init__(self, config: StatsConfig):
        self.config = config

    def output(self, stats: TradingStats):
        # print tables
        stats.main_results.show(self.config.currency_symbol)
        # CoinInsights.show(stats.coin_res, self.config.currency_symbol)
        # OpenTradeResult.show(stats.open_trade_res, self.config.currency_symbol)

        show_trade_anomalies(stats)

        show_signature()

        # plot graphs
        # if self.config.plots:
        #     plot_per_coin(stats.frame_with_signals, stats.df, self.config, stats.buypoints, stats.sellpoints)


class ConsoleColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def show_trade_anomalies(stats: TradingStats):

    trades = list(filter(lambda x: x.sell_reason == SellReason.STOPLOSS_AND_ROI, stats.trades))

    if len(trades) > 0:
        print_warning("WARNING: Stoploss and ROI reached for trade in single OHLCV")
        for trade in trades:
            print_warning(f"Trade opened at {trade.opened_at}")

def print_warning(text):
    print(f"{ConsoleColors.WARNING}{text}{ConsoleColors.ENDC}")
