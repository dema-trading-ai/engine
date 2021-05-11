# Files
from modules.setup.setup import SetupModule
from modules.algo.algo import AlgoModule
from modules.stats.stats import StatsModule
from modules.output.output import OutputModule


class MainController:

    def __init__(self):
        self.setup_module = SetupModule()
        self.algo_module = AlgoModule()
        self.stats_module = StatsModule()
        self.output_module = OutputModule()

    def run(self) -> None:
        ohlcv_pair_frames = self.setup_module.setup()
        frame_with_signals = self.algo_module.run(ohlcv_pair_frames)
        stats = self.stats_module.analyze(frame_with_signals)
        self.output_module.output(stats)
