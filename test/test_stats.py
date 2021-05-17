import math
from typing import Callable

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


def test_roi():
    """given `value of coin rises over ROI limit` should sell at ROI price"""
    # arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=0) \
        .add_entry(open=2, high=3, low=2, close=2, volume=1, buy=0, sell=0)

    fixture.trading_module_config.roi = {
            "0": 150
    }

    # act
    stats = fixture.create().analyze()

    # assert
    assert stats.main_results.end_capital == 245.025


def test_capital():
    """Given 'value of coin rises', 'capital' should 'rise same minus fee'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.end_capital == 196.02


def test_profit_percentage():
    """Given 'capital rises', 'profit_percentage' should 'rise accordingly'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.overall_profit_percentage, 96.02)


def test_capital_open_trade():
    """Given 'value of coin rises and open trade', 'capital' should 'rise same minus fee'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=0)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.end_capital == 198.
    assert len(stats.open_trade_res) == 1


def test_stoploss():
    """Given 'value of coin falls below stoploss', 'profit' should 'lower same minus fee'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=1)

    fixture.trading_module_config.stoploss = -25
    fixture.stats_config.stoploss = -25

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.end_capital == 73.5075


def test_dynamic_stoploss():
    """Given 'dynamic stoploss and value dips below stoploss',
    'end capital' should 'represent sold on stoploss price'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.trading_module_config.stoploss_type = "dynamic"

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0, stoploss=1) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=0, stoploss=1.5)
    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.end_capital == 73.5075


def test_dynamic_stoploss_high():
    """Given 'dynamic stoploss higher than open',
    'end capital' should 'represent sold on stoploss price'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.trading_module_config.stoploss_type = "dynamic"

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0, stoploss=1) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=0, stoploss=3)
    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.end_capital == 98.01


def test_dividing_assets():
    """Given 'multiple assets', '' should 'rise same minus fee'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=0)

    fixture.frame_with_signals['COIN2/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=0)

    fixture.trading_module_config.stoploss = 25
    fixture.stats_config.stoploss = 25

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.end_capital == 73.5075


def test_simple_realized_drawdown():
    """Given 'sell at half value', 'realized drawdown' should 'be half'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, -50.995)


def test_two_periods_realized_drawdown():
    """Given multiple trades, creating two separate drawdown
    periods, realized drawdown should be the drawdown of the biggest drawdown
    period"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=1) \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=5, low=1, close=5, volume=1, buy=0, sell=1) \
        .add_entry(open=5, high=5, low=5, close=5, volume=1, buy=1, sell=0) \
        .add_entry(open=5, high=5, low=2, close=2, volume=1, buy=0, sell=1) \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=4, low=2, close=4, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, -60.796)


def test_one_period_realized_drawdown():
    """Given multiple trades, creating one drawdown period, realized
    drawdown should be the drawdown of the entire period"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=5, high=5, low=5, close=5, volume=1, buy=1, sell=0) \
        .add_entry(open=5, high=5, low=3, close=3, volume=1, buy=0, sell=1) \
        .add_entry(open=3, high=3, low=3, close=3, volume=1, buy=1, sell=0) \
        .add_entry(open=3, high=4, low=3, close=4, volume=1, buy=0, sell=1) \
        .add_entry(open=4, high=4, low=4, close=4, volume=1, buy=1, sell=0) \
        .add_entry(open=4, high=4, low=1, close=1, volume=1, buy=0, sell=1) \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=5, low=1, close=5, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, -81.17039701198)


def test_n_trades():
    """Given 'trades where made', 
    'number of trades' should 'display correct amount' """
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE', 'COIN3/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=1) \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=1) \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0)

    # Win/Win/Open
    fixture.frame_with_signals['COIN2/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=1) \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=3, low=2, close=3, volume=1, buy=0, sell=1) \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0)

    # Loss/Loss/Open
    fixture.frame_with_signals['COIN3/BASE'] \
        .add_entry(open=3, high=3, low=3, close=3, volume=1, buy=1, sell=0) \
        .add_entry(open=3, high=3, low=2, close=2, volume=1, buy=0, sell=1) \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=1) \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.n_trades == 9
    assert stats.main_results.n_left_open_trades == 3
    assert stats.main_results.n_trades_with_loss == 3
    assert stats.main_results.n_consecutive_losses == 2


def test_positive_best_worst_trade():
    """Given one positive trade, 'best trade' should be trade profit,
    worst trade should be 0"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_win_single_trade, 96.02)
    assert math.isclose(stats.main_results.max_drawdown_single_trade, 0)


def test_negative_best_worst_trade():
    """Given one negative trade, 'worst trade' should be trade profit,
    best trade should be 0"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_win_single_trade, 0)
    assert math.isclose(stats.main_results.max_drawdown_single_trade, -50.995)


def test_best_worst_trade():
    """Given one negative trade, and one positive trade, 'worst trade' should be drawdown
    of negative trade, 'best trade' should be profit of positive trade"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=1) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_win_single_trade, 96.02)
    assert math.isclose(stats.main_results.max_drawdown_single_trade, -50.995)


StatsModuleFactory = Callable[[], StatsModule]


class StatsFixture:

    def __init__(self, pairs: list):
        self.stats_config = StatsConfig(
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

        self.trading_module_config = TradingModuleConfig(
            stoploss=stoploss,
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
