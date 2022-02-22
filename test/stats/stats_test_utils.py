import os
from datetime import datetime
import pytz
from pandas import DataFrame

from backtesting.strategy import Strategy
from modules.setup.config import create_config_from_dict
from modules.stats.stats import StatsModule
from modules.stats.trade import Trade, SellReason
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
        stripped_pairs = []
        for pair in pairs:
            stripped_pairs.append(pair.replace("/USDT", ""))

        raw_config = {
            "exchange": "binance",
            "timeframe": "30m",
            "max-open-trades": max_open_trades,
            "exposure-per-trade": exposure_per_trade,
            "starting-capital": STARTING_CAPITAL,
            "backtesting-from": "2020-01-01",
            "backtesting-to": "2020-07-01",
            "backtesting-till-now": False,
            "stoploss-type": "static",
            "stoploss": STOPLOSS,
            "roi": {"0": int(9999999999)},
            "pairs": stripped_pairs,
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

        self.config = create_config_from_dict(raw_config, False)
        self.frame_with_signals = MockPairFrame(pairs)

    def create(self):
        pair_df = {k: DataFrame.from_dict(v, orient='index', columns=OHLCV_INDICATORS) for k, v in
                   self.frame_with_signals.items()}

        trading_module = TradingModule(self.config, TestStrategy())
        return StatsModule(self.config, self.frame_with_signals, trading_module, pair_df)

    def create_with_strategy(self, strategy: Strategy):
        pair_df = {k: DataFrame.from_dict(v, orient='index', columns=OHLCV_INDICATORS) for k, v in
                   self.frame_with_signals.items()}

        trading_module = TradingModule(self.config, strategy)
        return StatsModule(self.config, self.frame_with_signals, trading_module, pair_df)


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


def date(timestamp) -> datetime:
    return datetime.fromtimestamp(timestamp / 1000)


def create_test_date(year=1970, month=1, day=1, hour=0, minute=0, second=0) -> datetime:
    return datetime.fromtimestamp(datetime(year, month, day, hour, minute, second, 0, pytz.UTC).timestamp())


def create_test_timestamp(year=1970, month=1, day=1, hour=0, minute=0, second=0) -> int:
    return datetime(year, month, day, hour, minute, second, 0, pytz.UTC).timestamp() * 1000
