import typing
from datetime import datetime

from pandas import DataFrame

from backtesting.backtesting import BackTesting
from backtesting.plots import plot_per_coin
from backtesting.results import CoinInsights, OpenTradeResult, show_signature, MainResults
from models.trade import Trade
from modules.setup.config import ConfigModule
from utils import calculate_worth_of_open_trades, default_empty_dict_dict


class AlgoModule(object):
    def __init__(self, history_data, config_module: ConfigModule, strategy):
    
        self.backtesting_module = BackTesting(history_data, config_module, strategy)
        self.config_module = config_module

    def run(self):
        return self.backtesting_module.start_backtesting()
