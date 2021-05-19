# Files
from modules.output import OutputModule
from modules.setup.config import ConfigModule
from modules.setup import SetupModule
from modules.stats.stats import StatsModule
from modules.stats.stats_config import to_stats_config
from modules.stats.tradingmodule import TradingModule
from modules.stats.tradingmodule_config import create_trading_module_config


class MainController:

    def __init__(self, args):
        self.config = ConfigModule(args)
        self.setup_module = SetupModule(self.config)

    def run(self) -> None:
        algo_module = self.setup_module.setup()
        df, dict_with_signals = algo_module.run()

        stats_config = to_stats_config(self.config)

        trading_module_config = create_trading_module_config(self.config)
        trading_module = TradingModule(trading_module_config)
        stats_module = StatsModule(stats_config, dict_with_signals, trading_module, df)

        stats = stats_module.analyze()

        OutputModule(stats_config).output(stats)
