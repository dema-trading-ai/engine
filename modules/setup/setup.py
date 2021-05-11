from pandas import DataFrame

from data.datamodule import DataModule
from modules.algo.algo import AlgoModule
from modules.setup.config import ConfigModule, print_pairs, load_strategy_from_config


class SetupModule(object):

    def __init__(self, config_module):
        self.config = config_module

    def setup(self) -> AlgoModule:
        print_pairs(self.config.raw_config)  # TODO fix mixed level of abstraction
        ohlcv_pair_frames = DataModule(self.config).load_historical_data()

        strategy = load_strategy_from_config(self.config.strategy_definition)

        return AlgoModule(ohlcv_pair_frames, self.config, strategy)
