import os

import pandas as pd
from pandas import DataFrame

from backtesting.strategy import Strategy
from modules.stats.stats import StatsModule
from modules.stats.stats_config import StatsConfig
from modules.stats.tradingmodule import TradingModule
from modules.stats.tradingmodule_config import TradingModuleConfig
from test.utils.signal_frame import MockPairFrame
from utils.utils import get_ohlcv_indicators
from modules.stats.trade import Trade, SellReason

os.environ["VERBOSITY"] = "quiet"  # disables printing of info and warning messages

StatsModuleFactory = [[], StatsModule]

max_open_trades = 3
exposure_per_trade = 1.
STARTING_CAPITAL = 100.
FEE_PERCENTAGE = 1

STOPLOSS = 100

OHLCV_INDICATORS = get_ohlcv_indicators()


class StatsFixture:

    def __init__(self, pairs: list):
        self.stats_config = StatsConfig(
            max_open_trades=max_open_trades,
            exposure_per_trade=exposure_per_trade,
            starting_capital=100,
            backtesting_from=1,
            backtesting_to=10,
            timeframe='1ms',
            btc_marketchange_ratio=1,
            btc_drawdown_ratio=1,
            fee=FEE_PERCENTAGE,

            stoploss=STOPLOSS,
            stoploss_type="static",
            currency_symbol="USDT",
            plots=False,
            tearsheet=False,
            export_result=False,

            mainplot_indicators=[],
            subplot_indicators=[],
            strategy_definition=object(),
            strategy_name='MyStrategy',
            randomize_pair_order=False
        )

        self.trading_module_config = TradingModuleConfig(
            stoploss=STOPLOSS,
            max_open_trades=max_open_trades,
            exposure_per_trade=exposure_per_trade,
            starting_capital=STARTING_CAPITAL,
            fee=FEE_PERCENTAGE,
            pairs=pairs,
            stoploss_type="static",
            roi={"0": int(9999999999)}
        )

        self.frame_with_signals = MockPairFrame(pairs)

    def create(self):
        pair_df = {k: pd.DataFrame.from_dict(v, orient='index', columns=OHLCV_INDICATORS) for k, v in
                   self.frame_with_signals.items()}

        trading_module = TradingModule(self.trading_module_config, TestStrategy())
        return StatsModule(self.stats_config, self.frame_with_signals, trading_module, pair_df)

    def create_with_strategy(self, strategy: Strategy):
        pair_df = {k: pd.DataFrame.from_dict(v, orient='index', columns=OHLCV_INDICATORS) for k, v in
                   self.frame_with_signals.items()}

        trading_module = TradingModule(self.trading_module_config, strategy)
        return StatsModule(self.stats_config, self.frame_with_signals, trading_module, pair_df)


class TestStrategy(Strategy):
    # Empty strategy used for testing purposes
    def generate_indicators(self, dataframe: DataFrame, additional_pairs=None) -> DataFrame:
        return dataframe

    def buy_signal(self, dataframe: DataFrame) -> DataFrame:
        return dataframe

    def sell_signal(self, dataframe: DataFrame) -> DataFrame:
        return dataframe


class CooldownStrategy(TestStrategy):
    # Addition to the testing strategy to test cooldowns
    def buy_cooldown(self, last_trade: Trade) -> int:
        cooldown = 0
        if last_trade.sell_reason == SellReason.STOPLOSS:
            cooldown = 2
        elif last_trade.sell_reason == SellReason.SELL_SIGNAL:
            cooldown = 5
        elif last_trade.sell_reason == SellReason.ROI:
            cooldown = 1
        return cooldown
