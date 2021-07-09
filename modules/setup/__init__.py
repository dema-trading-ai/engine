from modules.algo import AlgoModule
from modules.algo.backtesting import BackTesting
from modules.setup.config import print_pairs, load_strategy_from_config, get_additional_pairs, ConfigModule
from modules.setup.datamodule import DataModule


class SetupModule(object):

    def __init__(self, config_module: ConfigModule, data_module: DataModule):
        self.data_module = data_module
        self.config = config_module

    async def setup(self) -> AlgoModule:
        print_pairs(self.config.raw_config)  # TODO fix mixed level of abstraction
        ohlcv_pair_frames = await self.data_module.load_historical_data(self.config.pairs)

        strategy = load_strategy_from_config(self.config.strategy_definition)
        strategy.timeframe = self.config.timeframe

        additional_pairs = get_additional_pairs(strategy)
        additional_ohlcv_pair_frames = await self.data_module.load_historical_data(additional_pairs, check_backtesting_period=False)

        backtesting_module = BackTesting(ohlcv_pair_frames, self.config, strategy, additional_ohlcv_pair_frames)

        return AlgoModule(self.config, backtesting_module)
