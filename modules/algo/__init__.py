from modules.algo.backtesting import BackTesting
from modules.setup.config import ConfigModule


class AlgoModule(object):
    def __init__(self, config: ConfigModule, ohlcv_pair_frames, strategy, additional_ohlcv_pair_frames):
        self.ohlcv_pair_frames = ohlcv_pair_frames
        self.strategy = strategy
        self.additional_ohlcv_pair_frames = additional_ohlcv_pair_frames
        self.config = config

    def run(self):
        backtesting_module = BackTesting(self.ohlcv_pair_frames, self.config, self.strategy,
                                         self.additional_ohlcv_pair_frames)
        return backtesting_module.start_backtesting()
