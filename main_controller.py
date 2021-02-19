from backtesting.backtesting import BackTesting
from data.datamodule import DataModule
from data.tradingmodule import TradingModule


class MainController:

    def __init__(self, config):
        self.config = config
        self.trading_module = TradingModule(config)
        self.backtesting_module = BackTesting(self.trading_module, config)
        self.data_module = DataModule(config, self.backtesting_module)


