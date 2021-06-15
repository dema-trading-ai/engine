from modules.algo import AlgoModule
from modules.algo.backtesting import BackTesting
from modules.setup.config import print_pairs, load_strategy_from_config, ConfigModule
from modules.setup.datamodule import DataModule


class SetupModule(object):

    def __init__(self, config_module: ConfigModule):
        self.config = config_module

    async def setup(self) -> AlgoModule:
        print_pairs(self.config.raw_config)  # TODO fix mixed level of abstraction
        data_module = await DataModule.create(self.config)
        ohlcv_pair_frames = await data_module.load_historical_data()

        strategy = load_strategy_from_config(self.config.strategy_definition)
        backtesting_module = BackTesting(ohlcv_pair_frames, self.config, strategy)

        return AlgoModule(self.config, backtesting_module)
