import os

import pandas as pd

from modules.setup.config import create_config_from_dict
from modules.stats.stats import StatsModule
from modules.stats.tradingmodule import TradingModule
from test.utils.signal_frame import MockPairFrame
from utils.utils import get_ohlcv_indicators

os.environ["VERBOSITY"] = "quiet"  # disables printing of info and warning messages

StatsModuleFactory = [[], StatsModule]

max_open_trades = 3
exposure_per_trade = 100.
STARTING_CAPITAL = 100.
FEE_PERCENTAGE = 1

STOPLOSS = 100

OHLCV_INDICATORS = get_ohlcv_indicators()


class StatsFixture:

    def __init__(self, pairs: list):
        raw_config = {
            "exchange": "binance",
            "timeframe": "30m",
            "max-open-trades": max_open_trades,
            "exposure-per-trade": exposure_per_trade,
            "starting-capital": STARTING_CAPITAL,
            "backtesting-from": "2021-01-01",
            "backtesting-to": "2021-07-01",
            "backtesting-till-now": False,
            "stoploss-type": "static",
            "stoploss": STOPLOSS,
            "roi": {"0": int(9999999999)},
            "pairs": pairs,
            "randomize-pair-order": False,
            "currency": "USDT",
            "fee": FEE_PERCENTAGE,
            "strategy-name": "MyStrategy",
            "strategies-folder": "resources/setup/strategies",
            "plots": True,
            "tearsheet": False,
            "export-result": False,
            "mainplot_indicators": ["ema5", "ema21"],
            "subplot_indicators": [["volume"]]
        }

        self.config = create_config_from_dict(raw_config)

        self.frame_with_signals = MockPairFrame(pairs)

    def create(self):
        pair_df = {k: pd.DataFrame.from_dict(v, orient='index', columns=OHLCV_INDICATORS) for k, v in
                   self.frame_with_signals.items()}

        trading_module = TradingModule(self.config)
        return StatsModule(self.config, self.frame_with_signals, trading_module, pair_df)
