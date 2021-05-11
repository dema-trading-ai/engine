from backtesting.backtesting import BackTesting
from modules.setup.config import ConfigModule


class AlgoModule(object):
    def __init__(self, history_data, config_module: ConfigModule, strategy):
        self.backtesting_module = BackTesting(history_data, config_module, strategy)
        self.config_module = config_module

    def run(self):
        dict_with_signals = self.backtesting_module.start_backtesting()
        df = self.backtesting_module.df
        return df, dict_with_signals
