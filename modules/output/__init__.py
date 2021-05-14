from backtesting.plots import plot_per_coin
from backtesting.results import CoinInsights, OpenTradeResult, show_signature
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
        show_signature()

        # plot graphs
        # if self.config.plots:
        #     plot_per_coin(stats.frame_with_signals, stats.df, self.config, stats.buypoints, stats.sellpoints)