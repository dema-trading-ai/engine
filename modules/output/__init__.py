import dataclasses
import json
import os
import pandas as pd

from cli.print_utils import print_warning, print_error, print_info
from modules.output.plots_per_coin import plot_per_coin
from modules.output.equity_plot import equity_plot
from modules.output.results import show_signature, CoinInsights, LeftOpenTradeResult, show_mainresults
from modules.public.trading_stats import TradingStats
from modules.stats.stats_config import StatsConfig
from modules.stats.trade import SellReason
from modules.setup.config.strategy_definition import StrategyDefinition

FONT_BOLD = "\033[1m"
FONT_RESET = "\033[0m"


class OutputModule(object):
    config: StatsConfig

    def __init__(self, config: StatsConfig):
        self.config = config

    def output(self, stats: TradingStats, strategy_definition: StrategyDefinition):
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

        print_info("Logging trades to " + FONT_BOLD + f"data/backtesting-data/trades_log_{self.config.strategy_name}.json" + FONT_RESET + "...")
        log_trades(stats, self.config)

        # write orders to a  tearsheet
        if self.config.tearsheet and len(stats.trades):
            print_info("Logging trades to " + FONT_BOLD + "data/backtesting-data/tearsheet.xlsx" + FONT_RESET + "...")
            create_tearsheet(stats.trades)

        # plot graphs
        if self.config.plots:
            print_info("Creating plots in " + FONT_BOLD + "data/backtesting-data/plots" + FONT_RESET + "...")
            plot_per_coin(stats, config=self.config)
            equity_plot(stats.capital_per_timestamp, self.config.strategy_definition.strategy_name)
        print_info("Backtest finished!")

        # Export backtest result as JSON
        if self.config.export_result:
            print_info("Exporting backtest report to " + FONT_BOLD + "data/backtesting-data/backtest_result.json" + FONT_RESET + "...")
            export_backtest_result(stats, strategy_definition)

        show_signature()


def show_trade_anomalies(stats: TradingStats):
    trades = list(filter(lambda x: x.sell_reason == SellReason.STOPLOSS_AND_ROI, stats.trades))

    if len(trades) > 0:
        print_warning("Both Stoploss and ROI were triggered in the same candle, during the "
                      "following trade(s):")
        for trade in trades:
            print_warning(f"- {trade.opened_at} ==> {trade.closed_at}")
        print_warning("Profit for affected trades will be set to 0%")


def log_trades(stats: TradingStats, config: StatsConfig):
    trades_dict = {
        "max-open-trades": config.max_open_trades,
        "timeframe": config.timeframe,
        "fee-percentage": config.fee,
        "trades": {}
    }
    for i, trade in enumerate(stats.trades):
        trade_dict = {'status': trade.status,
                      'opened_at': trade.opened_at,
                      'closed_at': trade.closed_at,
                      'pair': trade.pair,
                      'open_price': trade.open,
                      'close_price': trade.close,
                      'fee_paid_open': trade.fee_paid_open,
                      'fee_paid_close': trade.fee_paid_close,
                      'fee_paid_total': trade.fee_paid_total,
                      'starting_amount': trade.starting_amount,
                      'capital': trade.capital,
                      'currency_amount': trade.currency_amount,
                      'sell_reason': trade.sell_reason}

        trades_dict["trades"][i] = trade_dict

    trades_json = json.dumps(trades_dict, indent=4, default=str)

    # remove the old trade log file. Can be removed in the future.
    try:
        os.remove('./data/backtesting-data/trades_log.json')
    except FileNotFoundError:
        pass

    with open(f'./data/backtesting-data/trades_log_{config.strategy_name}.json', 'w', encoding='utf-8') as f:
        f.write(trades_json)


def create_tearsheet(trades):
    dict_count = len(trades)
    df = pd.DataFrame(trades[0].__dict__, index=[0])
    for i in range(1, dict_count):
        df = df.append(trades[i].__dict__, ignore_index=True)

    df.to_excel('data/backtesting-data/tearsheet.xlsx')

    
def export_backtest_result(stats, strategy_definition):
    with open(f"data/backtesting-data/{strategy_definition.strategy_name}_backtest_result.json", 'w') as f:
        json.dump(dataclasses.asdict(stats.main_results), default=str, fp=f)

