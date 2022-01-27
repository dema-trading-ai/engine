import sys
from contextlib import asynccontextmanager
from typing import Generator

from optuna import Trial

from cli.print_utils import print_error
from modules.output import OutputModule
from modules.setup import ConfigModule, DataModule, SetupModule
from modules.stats.stats import StatsModule
from modules.stats.tradingmodule import TradingModule
from modules.stats.tradingmodule_config import create_trading_module_config


class BacktestRunner:
    def __init__(self, config: ConfigModule, data_module: DataModule, algo_module, df, strategy):
        self.data_module = data_module
        self.config = config
        self.algo_module = algo_module
        self.df = df
        self.strategy = strategy

    def run_backtest(self):
        pair_dicts, dict_with_signals = self.algo_module.run()
        trading_module = TradingModule(self.config)
        stats_module = StatsModule(self.config, dict_with_signals, trading_module, pair_dicts)
        return stats_module.analyze()

    def run_hyperopt_iteration(self, trial: Trial) -> float:
        self.strategy.trial = trial
        stats = self.run_backtest()
        try:
            return self.strategy.loss_function(stats)
        except NotImplementedError:
            print_error("The Loss function isn't implemented in your strategy. For an example loss function, check out"
                        " our documentation at docs.dematrading.ai.")
            sys.exit()

    def run_outputted_backtest(self):
        stats = self.run_backtest()
        OutputModule(self.config).output(stats, self.config.strategy_definition)


@asynccontextmanager
async def create_backtest_runner(args: object) -> Generator[BacktestRunner, None, None]:
    config = None
    try:
        config = await ConfigModule.create(args)
        data_module = await DataModule.create(config)
        setup_module = SetupModule(config, data_module)
        algo_module, df, strategy = await setup_module.setup()
        backtest_runner = BacktestRunner(config, data_module, algo_module, df, strategy)

        yield backtest_runner
    finally:
        if config is not None:
            await config.close()
