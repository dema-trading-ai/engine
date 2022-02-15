import math
from datetime import datetime
from datetime import timedelta

from test.stats.stats_test_utils import StatsFixture
from test.utils.signal_frame import TradeAction, DAILY, ONE_MIL


def test_multiple_periods_realized_drawdown_two_drawdown_periods():
    """Given multiple trades, creating two separate drawdown
    periods, realized drawdown should be the drawdown of the biggest drawdown
    period"""
    # Arrange
    fixture = StatsFixture(['COIN/USDT'])

    fixture.frame_with_signals['COIN/USDT'].test_scenario_down_10_up_100_down_75_three_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, -0.755, abs_tol=0.001)


def test_multiple_periods_realized_drawdown_one_drawdown_period():
    """Given multiple trades, creating one drawdown period, realized
    drawdown should be the drawdown of the entire period"""
    # Arrange
    fixture = StatsFixture(['COIN/USDT'])

    fixture.frame_with_signals['COIN/USDT'].test_scenario_up_100_down_20_down_75_three_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, -0.808, abs_tol=0.001)


def test_simple_realized_drawdown():
    """Given 'sell at half value', 'realized drawdown' should 'be half'"""
    # Arrange
    fixture = StatsFixture(['COIN/USDT'])

    fixture.frame_with_signals['COIN/USDT'].test_scenario_down_50_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, -0.51, abs_tol=0.01)


def test_simple_no_realized_drawdown():
    """Given 'no drawdown trades', 'realized drawdown' should 'none'"""
    # Arrange
    fixture = StatsFixture(['COIN/USDT', 'COIN2/USDT'])

    fixture.frame_with_signals['COIN/USDT'].test_scenario_up_50_one_trade()

    fixture.frame_with_signals['COIN2/USDT'].test_scenario_up_50_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, 0)


def test_multiple_periods_realized_drawdown():
    """Given coins with multiple trades over multiple drawdown periods, their combined
    'realised drawdown' should be a combination over these trades. It combines the tests
    defined in test_multiple_periods_realized_drawdown_*"""
    # Arrange
    fixture = StatsFixture(['COIN/USDT', 'COIN2/USDT', 'COIN3/USDT'])

    fixture.frame_with_signals['COIN/USDT'].test_scenario_down_10_up_100_down_75_three_trades()

    fixture.frame_with_signals['COIN2/USDT'].test_scenario_down_10_up_100_down_75_three_trades()

    fixture.frame_with_signals['COIN3/USDT'].test_scenario_up_100_down_20_down_75_three_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, -0.755, abs_tol=0.001)


def test_simple_seen_drawdown():
    """ Given 'sell at half value', 'seen drawdown' should 'be half'"""
    # Arrange
    fixture = StatsFixture(['COIN/USDT'])

    fixture.frame_with_signals['COIN/USDT'].test_scenario_down_50_one_trade(timestep=DAILY)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_seen_drawdown, -0.51, abs_tol=0.01)
    assert datetime.fromtimestamp(stats.main_results.drawdown_from / 1000) == datetime(year=2020, month=1, day=1)
    assert stats.main_results.drawdown_to == 0  # zero, because the drawdown hasn't ended yet
    assert datetime.fromtimestamp(stats.main_results.drawdown_at / 1000) == datetime(year=2020, month=1, day=2)


def test_simple_no_seen_drawdown():
    """ Given 'no drawdown trades', 'seen drawdown' should be equal to the fee (1%)"""
    # Arrange
    fixture = StatsFixture(['COIN/USDT'])

    fixture.frame_with_signals['COIN/USDT'].test_scenario_up_50_one_trade(timestep=DAILY)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_seen_drawdown, -0.01, abs_tol=0.01)
    assert datetime.fromtimestamp(stats.main_results.drawdown_from / 1000) == datetime(year=2020, month=1, day=1)
    assert datetime.fromtimestamp(stats.main_results.drawdown_to / 1000) == datetime(year=2020, month=1, day=2)
    assert datetime.fromtimestamp(stats.main_results.drawdown_at / 1000) == datetime(year=2020, month=1, day=1)


def test_multiple_periods_seen_drawdown_two_drawdown_periods():
    """ Given one trade, creating two separate drawdown
    periods, seen drawdown should be the drawdown of the biggest drawdown
    period, which in this case does not incorporate fees """
    # Arrange
    fixture = StatsFixture(['COIN/USDT'])

    fixture.frame_with_signals['COIN/USDT'].test_scenario_down_10_up_100_down_75_three_trades(timestep=DAILY)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_seen_drawdown, -0.755, abs_tol=0.001)
    assert datetime.fromtimestamp(stats.main_results.drawdown_from / 1000) == datetime(year=2020, month=1, day=4)
    assert stats.main_results.drawdown_to == 0
    assert datetime.fromtimestamp(stats.main_results.drawdown_at / 1000) == datetime(year=2020, month=1, day=6)


def test_multiple_periods_seen_drawdown_one_drawdown_period():
    """ Given one trade, creating one drawdown period, realized
    drawdown should be the drawdown of the entire period,
    including the buy and sell fees """
    # Arrange
    fixture = StatsFixture(['COIN/USDT'])

    fixture.frame_with_signals['COIN/USDT'].test_scenario_up_100_down_20_down_75_three_trades(timestep=DAILY)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, -0.808, abs_tol=0.001)
    assert datetime.fromtimestamp(stats.main_results.drawdown_from / 1000) == datetime(year=2020, month=1, day=2)
    assert stats.main_results.drawdown_to == 0
    assert datetime.fromtimestamp(stats.main_results.drawdown_at / 1000) == datetime(year=2020, month=1, day=6)


def test_multiple_periods_seen_drawdown_easy():
    """
    Given coins with multiple trades over one drawdown periods, their combined
    'seen drawdown' should be a combination over these trades, including the
    buy fee """
    # Arrange
    fixture = StatsFixture(['COIN/USDT', 'COIN2/USDT', 'COIN3/USDT'])

    fixture.frame_with_signals['COIN/USDT'].test_scenario_down_50_one_trade(timestep=DAILY)

    fixture.frame_with_signals['COIN2/USDT'].test_scenario_down_50_one_trade(timestep=DAILY)

    fixture.frame_with_signals['COIN3/USDT'].test_scenario_down_75_one_trade(timestep=DAILY)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_seen_drawdown, -0.591, abs_tol=0.001)
    assert datetime.fromtimestamp(stats.main_results.drawdown_from / 1000) == datetime(year=2020, month=1, day=1)
    assert stats.main_results.drawdown_to == 0
    assert datetime.fromtimestamp(stats.main_results.drawdown_at / 1000) == datetime(year=2020, month=1, day=2)


def test_multiple_periods_seen_drawdown():
    """ Given coins with multiple trades over more drawdown periods, their combined
    'seen drawdown' should be a combination over these trades"""
    # Arrange
    fixture = StatsFixture(['COIN/USDT', 'COIN2/USDT', 'COIN3/USDT'])

    fixture.frame_with_signals['COIN/USDT'].test_scenario_down_10_up_100_down_75_three_trades(timestep=DAILY)

    fixture.frame_with_signals['COIN2/USDT'].test_scenario_down_10_up_100_down_75_three_trades(timestep=DAILY)

    fixture.frame_with_signals['COIN3/USDT'].test_scenario_up_100_down_20_down_75_three_trades(timestep=DAILY)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_seen_drawdown, -0.755, abs_tol=0.001)
    assert datetime.fromtimestamp(stats.main_results.drawdown_from / 1000) == datetime(year=2020, month=1, day=4)
    assert stats.main_results.drawdown_to == 0
    assert datetime.fromtimestamp(stats.main_results.drawdown_at / 1000) == datetime(year=2020, month=1, day=6)


def test_drawdown_equality():
    """Given one coin, 'max seen/real drawdown' from main results should be equal
    to that of the coin insights"""
    # Arrange
    fixture = StatsFixture(['COIN/USDT'])

    fixture.frame_with_signals['COIN/USDT'].test_scenario_up_100_down_20_down_75_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_seen_drawdown, stats.coin_results[0].max_seen_drawdown)
    assert math.isclose(stats.main_results.max_realised_drawdown, stats.coin_results[0].max_realised_drawdown)


def test_seen_drawdown_equals_realised_drawdown():
    """Given one coin, 'max seen drawdown' should be the
    lowest seen drawdown and 'max realised drawdown' should be the lowest
    actual realised drawdown"""
    # Arrange
    fixture = StatsFixture(['COIN/USDT'])

    fixture.frame_with_signals['COIN/USDT'].test_scenario_down_50_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.coin_results[0].max_seen_drawdown == \
           stats.coin_results[0].max_realised_drawdown


def test_drawdown_simple():
    """Given one coin, 'max seen drawdown' should be the
    lowest seen drawdown and 'max realised drawdown' should be the lowest
    actual realised drawdown"""
    # Arrange
    fixture = StatsFixture(['COIN/USDT'])

    fixture.frame_with_signals['COIN/USDT'].test_scenario_up_100_down_20_down_75_one_trade(timestep=DAILY)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_results[0].max_seen_drawdown, -0.802)
    assert math.isclose(stats.coin_results[0].max_realised_drawdown, -0.60796, abs_tol=0.00001)
    assert datetime.fromtimestamp(stats.main_results.drawdown_from / 1000) == datetime(year=2020, month=1, day=2)
    assert stats.main_results.drawdown_to == 0
    assert datetime.fromtimestamp(stats.main_results.drawdown_at / 1000) == datetime(year=2020, month=1, day=4)


def test_drawdown_multiple_peaks():
    """Given multiple trades, 'max seen drawdown' should be the lowest seen drawdown
    of the combined trades"""
    # Arrange
    fixture = StatsFixture(['COIN/USDT'])

    fixture.frame_with_signals['COIN/USDT'].test_scenario_down_10_up_100_down_75_one_trade(timestep=DAILY)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_results[0].max_seen_drawdown, -0.7525)
    assert math.isclose(stats.coin_results[0].max_realised_drawdown, -0.558955)
    assert datetime.fromtimestamp(stats.main_results.drawdown_from / 1000) == datetime(year=2020, month=1, day=3)
    assert stats.main_results.drawdown_to == 0
    assert datetime.fromtimestamp(stats.main_results.drawdown_at / 1000) == datetime(year=2020, month=1, day=4)


def test_drawdown_multiple_pairs():
    """Given multiple pairs, 'max seen drawdown' should be the lowest seen drawdown
    of the different pairs combined"""
    # Arrange
    fixture = StatsFixture(['COIN/USDT', 'COIN2/USDT'])

    fixture.frame_with_signals['COIN/USDT'].test_scenario_down_10_up_100_down_75_three_trades(timestep=DAILY)
    fixture.frame_with_signals['COIN/USDT'].test_scenario_flat_no_trades(timestep=DAILY)
    fixture.frame_with_signals['COIN/USDT'].test_scenario_up_100_down_20_down_75_one_trade(timestep=DAILY)

    fixture.frame_with_signals['COIN2/USDT'].test_scenario_up_100_down_20_down_75_three_trades(timestep=DAILY)
    fixture.frame_with_signals['COIN2/USDT'].test_scenario_down_10_up_100_down_75_three_trades(timestep=DAILY)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_results[0].max_seen_drawdown, -0.903940399)
    assert math.isclose(stats.coin_results[0].max_realised_drawdown, -0.903940399)

    assert math.isclose(stats.coin_results[1].max_seen_drawdown, -0.9186056132492075)
    assert math.isclose(stats.coin_results[1].max_realised_drawdown, -0.9186056132492075)

    assert math.isclose(stats.main_results.max_seen_drawdown, -0.8576400119125371)
    assert math.isclose(stats.main_results.max_realised_drawdown, -0.8576400119125371)
    assert datetime.fromtimestamp(stats.main_results.drawdown_from / 1000) == datetime(year=2020, month=1, day=4)
    assert stats.main_results.drawdown_to == 0
    assert datetime.fromtimestamp(stats.main_results.drawdown_at / 1000) == datetime(year=2020, month=1, day=12)

    assert stats.main_results.n_trades_with_loss == 7
    assert stats.main_results.n_consecutive_losses == 4


def test_drawdown_with_stoploss_one_trade():
    """Given stoploss hit, coin insight drawdown should be correct"""
    # Arrange
    fixture = StatsFixture(['COIN/USDT'])

    fixture.frame_with_signals['COIN/USDT'].test_scenario_down_10_up_100_down_75_one_trade()

    fixture.config.stoploss = -50

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_results[0].max_seen_drawdown, -0.722222222222)
    assert math.isclose(stats.coin_results[0].max_realised_drawdown, -0.505, abs_tol=0.001)


def test_drawdown_with_stoploss_multiple_trades():
    """Given stoploss hit, coin insight drawdown should be correct"""
    # Arrange
    fixture = StatsFixture(['COIN/USDT'])

    fixture.frame_with_signals['COIN/USDT'].test_scenario_down_10_up_100_down_75_three_trades()

    fixture.config.stoploss = -50

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_results[0].max_seen_drawdown, -0.505, abs_tol=0.001)
    assert math.isclose(stats.coin_results[0].max_realised_drawdown, -0.505, abs_tol=0.001)


def test_seen_drawdown_up_down():
    """Given 'one trade', 'seen_drawdown' should 'reflect actual'"""
    # Arrange
    fixture = StatsFixture(['COIN/USDT'])

    fixture.frame_with_signals["COIN/USDT"] \
        .multiply_price(1, TradeAction.BUY) \
        .multiply_price(4) \
        .multiply_price(0.1, TradeAction.SELL)
    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.coin_results[0].max_seen_drawdown == -0.97525


def test_seen_drawdown_down():
    """Given 'one trade', 'seen_drawdown' should 'reflect actual'"""
    # Arrange
    fixture = StatsFixture(['COIN/USDT'])

    fixture.frame_with_signals["COIN/USDT"] \
        .multiply_price(1, TradeAction.BUY) \
        .multiply_price(0.1, TradeAction.SELL)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.coin_results[0].max_seen_drawdown == -0.90199


def test_longest_drawdowns():
    """Check both drawdowns on the same daily scenario, seen drawdown should be 3 days long and not ongoing,
    realised drawdown should be 2 days long and ongoing"""

    # Arrange
    fixture = StatsFixture(['COIN/USDT'])

    fixture.frame_with_signals['COIN/USDT'].test_scenario_down_10_up_100_down_75_three_trades(timestep=DAILY)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.longest_seen_drawdown['longest_drawdown'] == timedelta(days=3)
    assert stats.main_results.longest_seen_drawdown['is_ongoing'] is False
    assert stats.main_results.longest_realised_drawdown['longest_drawdown'] == timedelta(days=2)
    assert stats.main_results.longest_realised_drawdown['is_ongoing'] is True


def test_longest_drawdowns_short_period():
    """Check both drawdowns for a very short scenario (one millisecond per trade), should return a time difference of
    3 and 2 milliseconds for seen and realised drawdown respectively"""

    # Arrange
    fixture = StatsFixture(['COIN/USDT'])

    fixture.frame_with_signals['COIN/USDT'].test_scenario_down_10_up_100_down_75_three_trades(timestep=ONE_MIL)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.longest_seen_drawdown['longest_drawdown'] == timedelta(milliseconds=3)
    assert stats.main_results.longest_realised_drawdown['longest_drawdown'] == timedelta(milliseconds=2)


def test_longest_drawdown_no_trade():
    """Checks that drawdowns are handled when no trades are made, both drawdowns should return a timedelta of 0"""

    # Arrange
    fixture = StatsFixture(['COIN/USDT'])

    fixture.frame_with_signals['COIN/USDT'].test_scenario_flat_no_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.longest_seen_drawdown['longest_drawdown'] == timedelta(0)
    assert stats.main_results.longest_realised_drawdown['longest_drawdown'] == timedelta(0)


def test_longest_drawdown_trend_down():
    """Checks that the ongoing detection works as intended, seen drawdown should be ongoing"""

    # Arrange
    fixture = StatsFixture(['COIN/USDT'])

    fixture.frame_with_signals['COIN/USDT'].test_scenario_down_50_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.longest_seen_drawdown['is_ongoing'] is True


def test_longest_drawdown_trend_up():
    """Checks that the ongoing detection works as intended, seen drawdown should not be ongoing"""

    # Arrange
    fixture = StatsFixture(['COIN/USDT'])

    fixture.frame_with_signals['COIN/USDT'].test_scenario_up_50_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.longest_seen_drawdown['is_ongoing'] is False
