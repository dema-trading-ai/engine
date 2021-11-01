# Files
import sys
from typing import Tuple

from backtesting.strategy import Strategy
from modules.public.pairs_data import PairsData
from modules.setup.config import ConfigModule
from cli.print_utils import print_info, print_warning, print_error


# ======================================================================
# BackTesting class is responsible for processing the ticks (ohlcv-data)
# besides responsible for calculations
#
# © 2021 DemaTrading.ai
# ======================================================================
#
# These constants are used for displaying and
# emphasizing in commandline backtestresults


class BackTesting:

    def __init__(self, data: dict, config_module: ConfigModule, strategy: Strategy, additional_pairs_data):
        self.data = {}
        self.buypoints = {}
        self.sellpoints = {}
        self.df = {}
        self.config = config_module
        self.starting_capital = config_module.starting_capital
        self.currency_symbol = config_module.currency_symbol
        self.strategy = strategy
        self.data = data
        self.additional_pairs_data = additional_pairs_data
        self.backtesting_from = config_module.backtesting_from
        self.backtesting_to = config_module.backtesting_to

    def start_backtesting(self) -> Tuple[dict, dict]:
        print_info('Starting backtest...')

        data_dict = self.populate_signals()
        return self.df, data_dict

    def populate_signals(self) -> PairsData:
        """
        Method used for populating indicators / signals
        Populates indicators
        Populates buy signal
        Populates sell signal
        """
        data_dict = {}
        notify = False
        notify_reason = ""
        stoploss_type = self.config.stoploss_type

        print_info("Populating Indicators")
        for pair in self.data.keys():
            df = self.data[pair].copy()
            cleandf = df.dropna().copy()

            try:
                indicators = self.strategy.generate_indicators(cleandf, self.additional_pairs_data)
            except TypeError:
                indicators = self.strategy.generate_indicators(cleandf)

            indicators = self.strategy.buy_signal(indicators)
            indicators = self.strategy.sell_signal(indicators)
            indicators = indicators.append(df.loc[df["close"].isnull()]).sort_index()
            self.df[pair] = indicators.copy()
            if stoploss_type == "dynamic":
                stoploss = self.strategy.stoploss(indicators)
                if stoploss is None:  # stoploss not configured
                    notify = True
                    notify_reason = "not configured"
                elif 'stoploss' in stoploss.columns:
                    indicators['stoploss'] = stoploss['stoploss']
                else:  # stoploss wrongly configured
                    notify = True
                    notify_reason = "configured incorrectly"
            data_dict[pair] = indicators.to_dict('index')
            if not self.df[pair][['open', 'high', 'low', 'close', 'volume', 'pair']].equals(
                    df[['open', 'high', 'low', 'close', 'volume', 'pair']]
            ):
                print_error(
                    "Cannot set OHLCV data in strategy.")
                sys.exit()
        if notify:
            print_warning(f"Dynamic stoploss {notify_reason}. Using static stoploss of "
                          f"{self.config.stoploss}%.")
        if stoploss_type == 'standard':
            self.config.stoploss_type = 'static'
            print_warning(f"The use of 'standard' is deprecated. Using static stoploss of {self.config.stoploss}%.")
        return data_dict
