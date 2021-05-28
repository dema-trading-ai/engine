import pandas as pd

from modules.stats.stats import StatsModule
from modules.stats.stats_config import StatsConfig
from modules.stats.tradingmodule import TradingModule
from modules.stats.tradingmodule_config import TradingModuleConfig
from test.utils.signal_frame import MockPairFrame
from utils import get_ohlcv_indicators

StatsModuleFactory = [[], StatsModule]

max_open_trades = 3
STARTING_CAPITAL = 100.
FEE_PERCENTAGE = 1

STOPLOSS = 100

OHLCV_INDICATORS = get_ohlcv_indicators()


class StatsFixture:

    def __init__(self, pairs: list):
        self.stats_config = StatsConfig(
            max_open_trades=max_open_trades,
            starting_capital=100,
            backtesting_from=1,
            backtesting_to=10,
            btc_marketchange_ratio=1,
            fee=FEE_PERCENTAGE,

            stoploss=STOPLOSS,
            currency_symbol="USDT",
            plots=False,

            mainplot_indicator=[],
            subplot_indicator=[]
        )

        self.trading_module_config = TradingModuleConfig(
            stoploss=STOPLOSS,
            max_open_trades=max_open_trades,
            starting_capital=STARTING_CAPITAL,
            fee=FEE_PERCENTAGE,
            pairs=pairs,
            stoploss_type="standard",
            roi={"0": int(9999999999)}
        )

        self.frame_with_signals = MockPairFrame(pairs)

    def create(self):
        df = pd.DataFrame.from_dict(self.frame_with_signals, orient='index', columns=OHLCV_INDICATORS)
        trading_module = TradingModule(self.trading_module_config)
        return StatsModule(self.stats_config, self.frame_with_signals, trading_module, df)