from cli.print_utils import print_warning
from modules.output.results import show_signature
from modules.stats.stats_config import StatsConfig
from modules.stats.trade import SellReason
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


def show_trade_anomalies(stats: TradingStats):
    trades = list(filter(lambda x: x.sell_reason == SellReason.STOPLOSS_AND_ROI, stats.trades))

    if len(trades) > 0:
        print_warning("WARNING: Both Stoploss and ROI were triggered in the same candle")
        print_warning("during the following trade(s):")
        for trade in trades:
            print_warning(f"- {trade.opened_at} ==> {trade.closed_at}")
        print_warning("profit for affected trades will be set to 0%")
