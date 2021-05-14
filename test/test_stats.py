import math
from typing import Callable, Any

import pandas as pd

from data.tradingmodule import TradingModule
from data.tradingmodule_config import TradingModuleConfig
from modules.stats.stats import StatsModule
from modules.stats.stats_config import StatsConfig
from test.utils.signal_frame import MockPairFrame
from utils import get_ohlcv_indicators

max_open_trades = 3
STARTING_CAPITAL = 100.
FEE_PERCENTAGE = 1

stoploss = 1000

OHLCV_INDICATORS = get_ohlcv_indicators()


# TODO num tra

def test_roi():
    """given `value of coin rises over ROI limit` should sell at ROI price"""
    # arrange
    stats_config, trading_module_config, frame_with_signals, create_stats_module = get_default_config(['THREE'])

    frame_with_signals["THREE"] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=0)

    trading_module_config.roi = {
        "0": 50
    }

    # act
    stats = create_stats_module().analyze()

    # assert
    assert stats.main_results.end_capital == 147.015


def test_capital():
    """Given 'value of coin rises', 'capital' should 'rise same minus fee'"""
    # Arrange
    stats_config, trading_module_config, frame_with_signals, create_stats_module = get_default_config(['THREE'])

    frame_with_signals["THREE"] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=1)

    # Act
    stats = create_stats_module().analyze()

    # Assert
    assert stats.main_results.end_capital == 196.02


def test_profit_percentage():
    """Given 'capital rises', 'profit_percentage' should 'rise accordingly'"""
    # Arrange
    stats_config, trading_module_config, frame_with_signals, create_stats_module = get_default_config(['THREE'])

    frame_with_signals["THREE"] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=1)

    # Act
    stats = create_stats_module().analyze()

    # Assert
    assert math.isclose(stats.main_results.overall_profit_percentage, 96.02)


def test_capital_open_trade():
    """Given 'value of coin rises and open trade', 'capital' should 'rise same minus fee'"""
    # Arrange
    stats_config, trading_module_config, frame_with_signals, create_stats_module = get_default_config(['THREE'])

    frame_with_signals["THREE"] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=0)

    # Act
    stats = create_stats_module().analyze()

    # Assert
    assert stats.main_results.end_capital == 198.
    assert stats.main_results.end_capital == 198.
    assert len(stats.open_trade_res) == 1


def test_stoploss():
    """Given 'value of coin falls below stoploss', 'profit' should 'lower same minus fee'"""
    # Arrange
    stats_config, trading_module_config, frame_with_signals, create_stats_module = get_default_config(['THREE'])

    frame_with_signals["THREE"] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=1)

    trading_module_config.stoploss = 25
    stats_config.stoploss = 25

    # Act
    stats = create_stats_module().analyze()

    # Assert
    assert stats.main_results.end_capital == 73.5075


def test_dynamic_stoploss():
    """Given 'dynamic stoploss and value dips below stoploss',
    'end capital' should 'represent sold on stoploss price'"""
    # Arrange
    stats_config, trading_module_config, frame_with_signals, create_stats_module = get_default_config(['THREE'])

    trading_module_config.stoploss_type = "dynamic"

    frame_with_signals["THREE"] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0, stoploss=1) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=0, stoploss=1.5)
    # Act
    stats = create_stats_module().analyze()

    # Assert
    assert stats.main_results.end_capital == 73.5075


def test_dynamic_stoploss_high():
    """Given 'dynamic stoploss higher than open',
    'end capital' should 'represent sold on stoploss price'"""
    # Arrange
    stats_config, trading_module_config, frame_with_signals, create_stats_module = get_default_config(['THREE'])

    trading_module_config.stoploss_type = "dynamic"

    frame_with_signals["THREE"] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0, stoploss=1) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=0, stoploss=3)
    # Act
    stats = create_stats_module().analyze()

    # Assert
    assert stats.main_results.end_capital == 98.01


def test_dividing_assets():
    """Given 'multiple assets', '' should 'rise same minus fee'"""
    # Arrange
    stats_config, trading_module_config, frame_with_signals, create_stats_module = get_default_config(['THREE', "two"])

    frame_with_signals["THREE"] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=1)

    frame_with_signals["two"] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=1)

    trading_module_config.stoploss = 25
    stats_config.stoploss = 25

    # Act
    stats = create_stats_module().analyze()

    # Assert
    assert stats.main_results.end_capital == 73.5075


def test_drawdown():
    """Given 'sell at half value', 'realized drawdown' should 'be half'"""
    # Arrange
    stats_config, trading_module_config, frame_with_signals, create_stats_module = get_default_config(['THREE'])

    frame_with_signals["THREE"] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=1)

    # Act
    stats = create_stats_module().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, -50.995)


StatsModuleFactory = Callable[[], StatsModule]


def get_default_config(pairs: list[str]) -> tuple[StatsConfig, TradingModuleConfig, MockPairFrame, StatsModuleFactory]:
    stats_config = StatsConfig(
        max_open_trades=max_open_trades,
        starting_capital=100,
        backtesting_from=1,
        backtesting_to=10,
        btc_marketchange_ratio=1,
        fee=FEE_PERCENTAGE,

        stoploss=stoploss,
        currency_symbol="USDT",
        plots=False,

        plot_indicators1=[],
        plot_indicators2=[]
    )

    trading_module_config = TradingModuleConfig(
        stoploss=stoploss,
        max_open_trades=max_open_trades,
        starting_capital=STARTING_CAPITAL,
        fee=FEE_PERCENTAGE,
        pairs=pairs,
        stoploss_type="standard",
        roi={"0": int(9999999999)}
    )

    frame = MockPairFrame(pairs)

    def create_stats_module():
        trading_module = TradingModule(trading_module_config)
        df = pd.DataFrame.from_dict(frame, orient='index', columns=OHLCV_INDICATORS)
        return StatsModule(stats_config, frame, trading_module, df)

    return stats_config, trading_module_config, frame, create_stats_module
