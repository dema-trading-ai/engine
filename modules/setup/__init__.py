from backtesting.backtesting import BackTesting
from data.datamodule import DataModule
from modules.algo import AlgoModule
from modules.setup.config import print_pairs, load_strategy_from_config, ConfigModule


class SetupModule(object):

    def __init__(self, config_module: ConfigModule):
        self.config = config_module

    def setup(self) -> AlgoModule:
        print_pairs(self.config.raw_config)  # TODO fix mixed level of abstraction
        ohlcv_pair_frames = DataModule(self.config).load_historical_data()

        strategy = load_strategy_from_config(self.config.strategy_definition)
        backtesting_module = BackTesting(ohlcv_pair_frames, self.config, strategy)

        return AlgoModule(self.config, backtesting_module)
