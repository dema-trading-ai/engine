import math

from test.stats.stats_test_utils import StatsFixture
from test.utils.signal_frame import TradeAction


def test_multiple_periods_realized_drawdown_two_drawdown_periods():
    """Given multiple trades, creating two separate drawdown
    periods, realized drawdown should be the drawdown of the biggest drawdown
    period"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_10_up_100_down_75_three_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, -75.4975)


def test_multiple_periods_realized_drawdown_one_drawdown_period():
    """Given multiple trades, creating one drawdown period, realized
    drawdown should be the drawdown of the entire period"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_down_20_down_75_three_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, -80.7880798)


def test_simple_realized_drawdown():
    """Given 'sell at half value', 'realized drawdown' should 'be half'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_50_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, -50.995)


def test_simple_no_realized_drawdown():
    """Given 'no drawdown trades', 'realized drawdown' should 'none'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_50_one_trade()

    fixture.frame_with_signals['COIN2/BASE'].test_scenario_up_50_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, 0)


def test_multiple_periods_realized_drawdown():
    """Given coins with multiple trades over multiple drawdown periods, their combined
    'realised drawdown' should be a combination over these trades. It combines the tests
    defined in test_multiple_periods_realized_drawdown_*"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE', 'COIN3/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_10_up_100_down_75_three_trades()

    fixture.frame_with_signals['COIN2/BASE'].test_scenario_down_10_up_100_down_75_three_trades()

    fixture.frame_with_signals['COIN3/BASE'].test_scenario_up_100_down_20_down_75_three_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, -76.5727336801886)


def test_simple_seen_drawdown():
    """ Given 'sell at half value', 'seen drawdown' should 'be half'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_50_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_seen_drawdown, -50.995)


def test_simple_no_seen_drawdown():
    """ Given 'no drawdown trades', 'seen drawdown' should be equal to the fee (1%)"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_50_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_seen_drawdown, -1)
    

def test_multiple_periods_seen_drawdown_two_drawdown_periods():
    """ Given one trade, creating two separate drawdown
    periods, seen drawdown should be the drawdown of the biggest drawdown
    period, which in this case does not incorporate fees """
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_10_up_100_down_75_three_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_seen_drawdown, -75.4975)


def test_multiple_periods_seen_drawdown_one_drawdown_period():
    """ Given one trade, creating one drawdown period, realized
    drawdown should be the drawdown of the entire period,
    including the buy and sell fees """
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_down_20_down_75_three_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, -80.7880798)


def test_multiple_periods_seen_drawdown_easy():
    """
    Given coins with multiple trades over one drawdown periods, their combined
    'seen drawdown' should be a combination over these trades, including the
    buy fee """
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE', 'COIN3/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_50_one_trade()
    fixture.frame_with_signals['COIN2/BASE'].test_scenario_down_50_one_trade()
    fixture.frame_with_signals['COIN3/BASE'].test_scenario_down_75_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_seen_drawdown, -59.1625)


def test_multiple_periods_seen_drawdown():
    """ Given coins with multiple trades over more drawdown periods, their combined
    'seen drawdown' should be a combination over these trades"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE', 'COIN3/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_10_up_100_down_75_three_trades()
    fixture.frame_with_signals['COIN2/BASE'].test_scenario_down_10_up_100_down_75_three_trades()
    fixture.frame_with_signals['COIN3/BASE'].test_scenario_up_100_down_20_down_75_three_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_seen_drawdown, -75.4975)


def test_drawdown_simple():
    """Given one coin, 'max seen drawdown' should be the
    lowest seen drawdown and 'max realised drawdown' should be the lowest
    actual realised drawdown"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_down_20_down_75_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_res[0].max_seen_drawdown, -80.2)


def test_drawdown_multiple_peaks():
    """Given multiple trades, 'max seen drawdown' should be the lowest seen drawdown
    of the combined trades"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_10_up_100_down_75_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_res[0].max_seen_drawdown, -75.25)


def test_drawdown_multiple_pairs():
    """Given multiple pairs, 'max seen drawdown' should be the lowest seen drawdown
    of the different pairs combined"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_10_up_100_down_75_three_trades()
    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_down_20_down_75_one_trade()

    fixture.frame_with_signals['COIN2/BASE'].test_scenario_up_100_down_20_down_75_three_trades()
    fixture.frame_with_signals['COIN2/BASE'].test_scenario_down_10_up_100_down_75_three_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_res[0].max_seen_drawdown, -90.3940399)

    assert math.isclose(stats.coin_res[1].max_seen_drawdown, -83.22282373767418)

    assert math.isclose(stats.main_results.max_seen_drawdown, -75.742525)


def test_seen_drawdown_up_down():
    """Given 'one trade', 'seen_drawdown' should 'reflect actual'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals["COIN/BASE"] \
        .multiply_price(1, TradeAction.BUY) \
        .multiply_price(4) \
        .multiply_price(0.1, TradeAction.SELL)
    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_res[0].max_seen_drawdown, -90.1)


def test_seen_drawdown_down():
    """Given 'one trade', 'seen_drawdown' should 'reflect actual'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals["COIN/BASE"] \
        .multiply_price(1, TradeAction.BUY) \
        .multiply_price(0.1, TradeAction.SELL)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.coin_res[0].max_seen_drawdown == -90.199
