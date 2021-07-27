import pandas as pd

from modules.stats.stats import StatsModule
from modules.stats.stats_config import StatsConfig
from modules.stats.tradingmodule import TradingModule
from modules.stats.tradingmodule_config import TradingModuleConfig
from test.utils.signal_frame import MockPairFrame
from utils.utils import get_ohlcv_indicators

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
            btc_marketchange_ratio=1,
            btc_drawdown_ratio=1,
            fee=FEE_PERCENTAGE,

            stoploss=STOPLOSS,
            stoploss_type="standard",
            currency_symbol="USDT",
            plots=False,
            tearsheet=False,

            mainplot_indicators=[],
            subplot_indicators=[]
        )

        self.trading_module_config = TradingModuleConfig(
            stoploss=STOPLOSS,
            max_open_trades=max_open_trades,
            exposure_per_trade=exposure_per_trade,
            starting_capital=STARTING_CAPITAL,
            fee=FEE_PERCENTAGE,
            pairs=pairs,
            stoploss_type="standard",
            roi={"0": int(9999999999)}
        )

        self.frame_with_signals = MockPairFrame(pairs)

    def create(self):
        pair_df = {k: pd.DataFrame.from_dict(v, orient='index', columns=OHLCV_INDICATORS) for k, v in
                   self.frame_with_signals.items()}

        trading_module = TradingModule(self.trading_module_config)
        return StatsModule(self.stats_config, self.frame_with_signals, trading_module, pair_df)
