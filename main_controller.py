# Files
from data.tradingmodule import TradingModule
from modules.output import OutputModule
from modules.setup.config import ConfigModule
from modules.setup import SetupModule
from modules.stats.stats import StatsModule
from modules.stats.stats_config import to_stats_config


class MainController:

    def __init__(self):
        self.config = ConfigModule()
        self.setup_module = SetupModule(self.config)
        self.output_module = OutputModule()

    def run(self) -> None:
        algo_module = self.setup_module.setup()
        df, dict_with_signals = algo_module.run()

        stats_config = to_stats_config(self.config)

        stats_module = StatsModule(stats_config, dict_with_signals, TradingModule(self.config.raw_config), df)

        stats_module.analyze()
