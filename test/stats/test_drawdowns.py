import math

from test.stats.stats_test_utils import StatsFixture


def test_multiple_periods_realized_drawdown_v1():
    """Given multiple trades, creating two separate drawdown
    periods, realized drawdown should be the drawdown of the biggest drawdown
    period"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1.5, close=1.5, volume=1, buy=0, sell=1) \
        .add_entry(open=1.5, high=1.5, low=1.5, close=1.5, volume=1, buy=1, sell=0) \
        .add_entry(open=1.5, high=6, low=1.5, close=6, volume=1, buy=0, sell=1) \
        .add_entry(open=6, high=6, low=6, close=6, volume=1, buy=1, sell=0) \
        .add_entry(open=6, high=6, low=3, close=3, volume=1, buy=0, sell=1) \
        .add_entry(open=3, high=3, low=3, close=3, volume=1, buy=1, sell=0) \
        .add_entry(open=3, high=4, low=3, close=4, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, -50.995)


def test_multiple_periods_realized_drawdown_v2():
    """Given multiple trades, creating two separate drawdown
    periods, realized drawdown should be the drawdown of the biggest drawdown
    period"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=4, high=4, low=4, close=4, volume=1, buy=1, sell=0) \
        .add_entry(open=4, high=4, low=1, close=1, volume=1, buy=0, sell=1) \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=5, low=1, close=5, volume=1, buy=0, sell=1) \
        .add_entry(open=5, high=5, low=5, close=5, volume=1, buy=1, sell=0) \
        .add_entry(open=5, high=5, low=3, close=3, volume=1, buy=0, sell=1) \
        .add_entry(open=3, high=3, low=3, close=3, volume=1, buy=1, sell=0) \
        .add_entry(open=3, high=6, low=3, close=6, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, -75.4975)


def test_multiple_periods_realized_drawdown_v3():
    """Given multiple trades, creating one drawdown period, realized
    drawdown should be the drawdown of the entire period"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=6, high=6, low=6, close=6, volume=1, buy=1, sell=0) \
        .add_entry(open=6, high=6, low=4, close=4, volume=1, buy=0, sell=1) \
        .add_entry(open=4, high=4, low=4, close=4, volume=1, buy=1, sell=0) \
        .add_entry(open=4, high=5, low=4, close=5, volume=1, buy=0, sell=1) \
        .add_entry(open=5, high=5, low=5, close=5, volume=1, buy=1, sell=0) \
        .add_entry(open=5, high=5, low=2, close=2, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, -68.617328354)


def test_simple_realized_drawdown():
    """Given 'sell at half value', 'realized drawdown' should 'be half'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=1)

    fixture.frame_with_signals['COIN2/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1.5, close=1.5, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, -38.74375)


def test_simple_no_realized_drawdown():
    """Given 'no drawdown trades', 'realized drawdown' should 'none'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=1)

    fixture.frame_with_signals['COIN2/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, 0)


def test_multiple_periods_realized_drawdown():
    """Given coins with multiple trades over multiple drawdown periods, their combined
    'realised drawdown' should be a combination over these trades. It combines the tests
    defined in test_drawdowns (v1, v2, v3)"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE', 'COIN3/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1.5, close=1.5, volume=1, buy=0, sell=1) \
        .add_entry(open=1.5, high=1.5, low=1.5, close=1.5, volume=1, buy=1, sell=0) \
        .add_entry(open=1.5, high=6, low=1.5, close=6, volume=1, buy=0, sell=1) \
        .add_entry(open=6, high=6, low=6, close=6, volume=1, buy=1, sell=0) \
        .add_entry(open=6, high=6, low=3, close=3, volume=1, buy=0, sell=1) \
        .add_entry(open=3, high=3, low=3, close=3, volume=1, buy=1, sell=0) \
        .add_entry(open=3, high=4, low=3, close=4, volume=1, buy=0, sell=1)

    fixture.frame_with_signals['COIN2/BASE'] \
        .add_entry(open=4, high=4, low=4, close=4, volume=1, buy=1, sell=0) \
        .add_entry(open=4, high=4, low=1, close=1, volume=1, buy=0, sell=1) \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=5, low=1, close=5, volume=1, buy=0, sell=1) \
        .add_entry(open=5, high=5, low=5, close=5, volume=1, buy=1, sell=0) \
        .add_entry(open=5, high=5, low=3, close=3, volume=1, buy=0, sell=1) \
        .add_entry(open=3, high=3, low=3, close=3, volume=1, buy=1, sell=0) \
        .add_entry(open=3, high=6, low=3, close=6, volume=1, buy=0, sell=1)

    fixture.frame_with_signals['COIN3/BASE'] \
        .add_entry(open=6, high=6, low=6, close=6, volume=1, buy=1, sell=0) \
        .add_entry(open=6, high=6, low=4, close=4, volume=1, buy=0, sell=1) \
        .add_entry(open=4, high=4, low=4, close=4, volume=1, buy=1, sell=0) \
        .add_entry(open=4, high=5, low=4, close=5, volume=1, buy=0, sell=1) \
        .add_entry(open=5, high=5, low=5, close=5, volume=1, buy=1, sell=0) \
        .add_entry(open=5, high=5, low=2, close=2, volume=1, buy=0, sell=1) \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=3, low=2, close=3, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, -50.995)


def test_simple_seen_drawdown():
    """ Given 'sell at half value', 'seen drawdown' should 'be half'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_seen_drawdown, -50.995)


def test_simple_no_seen_drawdown():
    """ Given 'no drawdown trades', 'seen drawdown' should 'none'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=1)

    fixture.frame_with_signals['COIN2/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_seen_drawdown, 0)


def test_multiple_periods_seen_drawdown_v1():
    """ Given one trade, creating two separate drawdown
    periods, seen drawdown should be the drawdown of the biggest drawdown
    period, which in this case does not incorporate fees """
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=0) \
        .add_entry(open=1, high=6, low=1, close=6, volume=1, buy=0, sell=0) \
        .add_entry(open=6, high=6, low=2, close=2, volume=1, buy=0, sell=0) \
        .add_entry(open=2, high=4, low=2, close=4, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_seen_drawdown, -66.66666666666667)


def test_multiple_periods_seen_drawdown_v2():
    """
    Given one trade, creating two separate drawdown
    periods, seen drawdown should be the drawdown of the biggest drawdown
    period, including the buy fee in this case """
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=4, high=4, low=4, close=4, volume=1, buy=1, sell=0) \
        .add_entry(open=4, high=4, low=1, close=1, volume=1, buy=0, sell=0) \
        .add_entry(open=1, high=6, low=1, close=6, volume=1, buy=0, sell=0) \
        .add_entry(open=6, high=6, low=3, close=3, volume=1, buy=0, sell=0) \
        .add_entry(open=3, high=6, low=3, close=6, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_seen_drawdown, -75.25)


def test_multiple_periods_seen_drawdown_v3():
    """ Given one trade, creating one drawdown period, realized
    drawdown should be the drawdown of the entire period,
    including the buy and sell fees """
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=6, high=6, low=6, close=6, volume=1, buy=1, sell=0) \
        .add_entry(open=6, high=6, low=4, close=4, volume=1, buy=0, sell=0) \
        .add_entry(open=4, high=5, low=4, close=5, volume=1, buy=0, sell=0) \
        .add_entry(open=5, high=5, low=2, close=2, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, -67.33)


def test_multiple_periods_seen_drawdown_easy():
    """
    Given coins with multiple trades over one drawdown periods, their combined
    'seen drawdown' should be a combination over these trades, including the
    buy fee """
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE', 'COIN3/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=1, high=6, low=1, close=6, volume=1, buy=1, sell=0) \
        .add_entry(open=6, high=6, low=2, close=2, volume=1, buy=0, sell=0)

    fixture.frame_with_signals['COIN2/BASE'] \
        .add_entry(open=1, high=6, low=1, close=6, volume=1, buy=1, sell=0) \
        .add_entry(open=6, high=6, low=3, close=3, volume=1, buy=0, sell=0)

    fixture.frame_with_signals['COIN3/BASE'] \
        .add_entry(open=4, high=5, low=4, close=5, volume=1, buy=1, sell=0) \
        .add_entry(open=5, high=5, low=2, close=2, volume=1, buy=0, sell=0)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_seen_drawdown, -59.3)


def test_multiple_periods_seen_drawdown():
    """ Given coins with multiple trades over more drawdown periods, their combined
    'seen drawdown' should be a combination over these trades"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE', 'COIN3/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=0) \
        .add_entry(open=1, high=6, low=1, close=6, volume=1, buy=0, sell=0) \
        .add_entry(open=6, high=6, low=2, close=2, volume=1, buy=0, sell=0) \
        .add_entry(open=2, high=4, low=2, close=4, volume=1, buy=0, sell=0)

    fixture.frame_with_signals['COIN2/BASE'] \
        .add_entry(open=4, high=4, low=4, close=4, volume=1, buy=1, sell=0) \
        .add_entry(open=4, high=4, low=1, close=1, volume=1, buy=0, sell=0) \
        .add_entry(open=1, high=6, low=1, close=6, volume=1, buy=0, sell=0) \
        .add_entry(open=6, high=6, low=3, close=3, volume=1, buy=0, sell=0) \
        .add_entry(open=3, high=6, low=3, close=6, volume=1, buy=0, sell=0)

    fixture.frame_with_signals['COIN3/BASE'] \
        .add_entry(open=6, high=6, low=6, close=6, volume=1, buy=1, sell=0) \
        .add_entry(open=6, high=6, low=2, close=2, volume=1, buy=0, sell=0) \
        .add_entry(open=2, high=8, low=2, close=8, volume=1, buy=0, sell=0) \
        .add_entry(open=8, high=8, low=2, close=2, volume=1, buy=0, sell=0) \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=0, sell=0)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_seen_drawdown, -64.28571428571428)