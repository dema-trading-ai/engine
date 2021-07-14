from contextlib import asynccontextmanager
from typing import Generator

from optuna import Trial

from modules.output import OutputModule
from modules.setup import ConfigModule, DataModule, SetupModule
from modules.stats.stats import StatsModule
from modules.stats.tradingmodule import TradingModule
from modules.stats.tradingmodule_config import create_trading_module_config


class BacktestRunner:
    def __init__(self, config: ConfigModule, data_module: DataModule, algo_module, df, strategy, stats_config):
        self.data_module = data_module
        self.module = config
        self.stats_config = stats_config
        self.trading_module_config = create_trading_module_config(config)
        self.algo_module = algo_module
        self.df = df
        self.strategy = strategy

    def execute_backtest(self):
        df2, dict_with_signals = self.algo_module.run()
        trading_module = TradingModule(self.trading_module_config)
        stats_module = StatsModule(self.stats_config, dict_with_signals, trading_module, df2)
        return stats_module.analyze()

    def run_hyperopt_iteration(self, trial: Trial) -> float:
        self.strategy.trial = trial
        stats = self.execute_backtest()
        return self.strategy.loss_function(stats)

    def execute_outputted_backtest(self):
        stats = self.execute_backtest()
        OutputModule(self.stats_config).output(stats)


@asynccontextmanager
async def create_backtest_runner(args: object) -> Generator[BacktestRunner, None, None]:
    config_module = None
    try:
        config_module = await ConfigModule.create(args)
        data_module = await DataModule.create(config_module)
        setup_module = SetupModule(config_module, data_module)
        algo_module, df, strategy, stats_config = await setup_module.setup()
        backtest_runner = BacktestRunner(config_module, data_module, algo_module, df, strategy, stats_config)

        yield backtest_runner
    finally:
        if config_module is not None:
            await config_module.close()
