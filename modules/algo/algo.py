from pandas import DataFrame

from backtesting.backtesting import BackTesting
from modules.setup.config import ConfigModule


class AlgoModule(object):
    def __init__(self, config_module: ConfigModule):
        self.backtesting_module = BackTesting()
        self.config_module = config_module

    def run(self, frame) -> dict[str, DataFrame]:
        self.backtesting_module.start_backtesting(frame,
                                                  self.config_module.backtesting_from,
                                                  self.config_module.backtesting_to,
                                                  self.config_module.btc_marketchange_ratio)

