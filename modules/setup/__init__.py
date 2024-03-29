from typing import Tuple

from backtesting.strategy import Strategy
from modules.algo import AlgoModule
from modules.setup.config import print_pairs, get_additional_pairs, ConfigModule
from modules.setup.config.load_strategy import load_strategy_from_config
from modules.setup.datamodule import DataModule
from utils.utils import parse_timeframe


class SetupModule(object):

    def __init__(self, config_module: ConfigModule, data_module: DataModule):
        self.data_module = data_module
        self.config = config_module

    async def setup(self) -> Tuple[AlgoModule, dict, Strategy]:
        print_pairs(self.config.pairs)
        ohlcv_pair_frames = await self.data_module.load_historical_data(self.config.pairs)

        strategy = load_strategy_from_config(self.config.strategy_definition)

        strategy.timeframe = self.config.timeframe

        additional_pairs = get_additional_pairs(strategy)
        additional_ohlcv_pair_frames = await self.data_module.load_historical_data(additional_pairs,
                                                                                   check_backtesting_period=False)

        # Reset original timeframe
        self.config.timeframe = strategy.timeframe
        self.config.timeframe_ms = parse_timeframe(strategy.timeframe)

        btc_marketchange_ratio, btc_drawdown_ratio = await self.data_module.load_btc_baseline()
        self.config.btc_marketchange_ratio = btc_marketchange_ratio
        self.config.btc_drawdown_ratio = btc_drawdown_ratio

        return AlgoModule(self.config, ohlcv_pair_frames, strategy,
                          additional_ohlcv_pair_frames), ohlcv_pair_frames, strategy
