from modules.algo.backtesting import BackTesting
from modules.setup.config import ConfigModule


class AlgoModule(object):
    def __init__(self, config_module: ConfigModule, backtesting_module: BackTesting):
        self.backtesting_module = backtesting_module
        self.config_module = config_module

    def run(self):
        dict_with_signals = self.backtesting_module.start_backtesting()
        df = self.backtesting_module.df
        return df, dict_with_signals
