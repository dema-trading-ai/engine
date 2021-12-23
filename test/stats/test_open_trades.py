import math

from datetime import datetime

from test.stats.stats_test_utils import StatsFixture


def test_open_trades_pair():
    """Given a left open trade, pair should match the coin pair"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_50_one_trade_no_sell()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.open_trade_results[0].pair == 'COIN/BASE'


def test_open_trades_profit_percentage_positive():
    """Given a profiting left open trade, profit percentage should be correct, including buy fee"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_one_trade_no_sell()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.open_trade_results[0].curr_profit_percentage == 98


def test_open_trades_profit_percentage_negative():
    """Given a losing left open trade, profit percentage should be correct, including buy fee"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_50_one_trade_no_sell()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.open_trade_results[0].curr_profit_percentage == -50.5


def test_open_trades_profit_positive():
    """Given a profiting left open trade, profit should be correct, including buy fee"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_one_trade_no_sell()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.open_trade_results[0].curr_profit == 98


def test_open_trades_profit_negative():
    """Given a losing left open trade, profit should be correct, including buy fee"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_50_one_trade_no_sell()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.open_trade_results[0].curr_profit == -50.5


def test_open_trades_drawdown_positive():
    """Given a profiting left open trade, max_seen_drawdown should be equal to fee"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_one_trade_no_sell()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.open_trade_results[0].max_seen_drawdown, -1)
    assert math.isclose(stats.main_results.max_seen_drawdown, stats.open_trade_results[0].max_seen_drawdown)


def test_open_trades_drawdown_negative():
    """Given a losing left open trade, max_seen_drawdown should be correct, including buy fee"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=0)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.open_trade_results[0].max_seen_drawdown == -50.5
    assert stats.main_results.max_seen_drawdown == stats.open_trade_results[0].max_seen_drawdown


def test_open_trades_opened_at():
    """Given a left open trade, opened_at should be timestep 1"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_one_trade_no_sell()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert datetime.fromtimestamp(stats.open_trade_results[0].opened_at.timestamp()) == datetime(year=2020, month=1, day=1)


def test_open_trades_opened_at_timestep_three():
    """Given a left open trade, opened_at should be timestep 3"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_one_trade()
    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_one_trade_no_sell()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert datetime.fromtimestamp(stats.open_trade_results[0].opened_at.timestamp()) == datetime(year=2020, month=1, day=3)
