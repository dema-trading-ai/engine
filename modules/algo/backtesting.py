# Libraries
from tqdm import tqdm
from rich import print as print_rich

# Files
from backtesting.strategy import Strategy
from modules.pairs_data import PairsData
from modules.setup.config import ConfigModule


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
    data = {}
    buypoints = {}
    sellpoints = {}
    df = {}

    def __init__(self, data: dict, config_module: ConfigModule, strategy: Strategy):
        self.config = config_module
        self.starting_capital = config_module.starting_capital
        self.currency_symbol = config_module.currency_symbol
        self.strategy = strategy
        self.data = data
        self.backtesting_from = config_module.backtesting_from
        self.backtesting_to = config_module.backtesting_to
        self.btc_marketchange_ratio = config_module.btc_marketchange_ratio

    def start_backtesting(self) -> PairsData:
        print_rich('[INFO] Starting backtest...')

        data_dict = self.populate_signals()
        return data_dict

    def populate_signals(self) -> PairsData:
        """
        Method used for populating indicators / signals
        Populates indicators
        Populates buy signal
        Populates sell signal
        :return: dict containing OHLCV data per pair
        """
        data_dict = {}
        notify = False
        notify_reason = ""
        stoploss_type = self.config.stoploss_type

        for pair in tqdm(self.data.keys(), desc="[INFO] Populating Indicators",
                         total=len(self.data.keys()), ncols=75):
            df = self.data[pair]
            indicators = self.strategy.generate_indicators(df)
            indicators = self.strategy.buy_signal(indicators)
            indicators = self.strategy.sell_signal(indicators)
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
        if notify:
            print_rich(
                f"[WARNING] [bright_yellow]Dynamic stoploss {notify_reason}. Using standard "
                f"stoploss of {self.config.stoploss}%.[/bright_yellow]")
        return data_dict
