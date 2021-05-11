# Files
from data.tradingmodule import TradingModule
from modules.setup.config import ConfigModule
from modules.setup.setup import SetupModule
from modules.stats.stats import StatsModule
from modules.stats.stats_config import toStatsConfig
from modules.output.output import OutputModule


class MainController:

    def __init__(self):
        self.config = ConfigModule()
        self.setup_module = SetupModule(self.config)
        self.output_module = OutputModule()

    def run(self) -> None:
        algo_module = self.setup_module.setup()
        dict_with_signals = algo_module.run()

        statsConfig = toStatsConfig(ConfigModule)
        stats_module = StatsModule(statsConfig, dict_with_signals, TradingModule(self.config.raw_config))

        stats = self.stats_module.analyze(dict_with_signals)
        self.output_module.output(stats)
