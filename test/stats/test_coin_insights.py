import math
from test.stats.stats_test_utils import StatsFixture
from test.utils.signal_frame import TradeAction


def test_fee_equals_stoploss():
    """Opening trade and fee is equal to stoploss, 
    'worst trade profit percentage' should be equal to 2x fee"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=0, sell=0)

    fixture.trading_module_config.stoploss = -1
    fixture.stats_config.stoploss = -1

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_res[0].total_profit_percentage, -1.99)

def test_worst_trade():
    """Given only losing trades, 'worst trade' should be worst of all trades"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE', 'COIN3/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1.75, close=1.75, volume=1, buy=0, sell=1)

    fixture.frame_with_signals['COIN2/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1.5, close=1.5, volume=1, buy=0, sell=1)

    fixture.frame_with_signals['COIN3/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1.25, close=1.25, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_res[-1].total_profit_percentage, -38.74375)
    assert math.isclose(stats.main_results.worst_trade, -38.74375)

def test_best_trade():
    """Given only winning trades, 'worst trade' should be worst of all trades"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE', 'COIN3/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=1.25, low=1, close=1.25, volume=1, buy=0, sell=1)

    fixture.frame_with_signals['COIN2/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=1.50, low=1, close=1.50, volume=1, buy=0, sell=1)

    fixture.frame_with_signals['COIN3/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=1.75, low=1, close=1.75, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_res[-1].total_profit_percentage, 71.5175)
    assert math.isclose(stats.main_results.best_trade, 71.5175)

def test_best_worst_trade_only_wins():
    """Given only winning trades, 'worst trade' should be worst of all trades"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=1.25, low=1, close=1.25, volume=1, buy=0, sell=1)

    fixture.frame_with_signals['COIN2/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=1.50, low=1, close=1.50, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.best_trade, 47.015)
    assert math.isclose(stats.main_results.worst_trade, 22.5125)

def test_best_worst_trade_only_losses():
    """Given only winning trades, 'worst trade' should be worst of all trades"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1.75, close=1.75, volume=1, buy=0, sell=1)

    fixture.frame_with_signals['COIN2/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1.5, close=1.5, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.best_trade, -14.24125)
    assert math.isclose(stats.main_results.worst_trade, -26.4925)


def test_marketchange():
    """Given coins with upward and downward trends, 'market change' should be 
    change between close value of first and last tick"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=1) \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=6, low=1, close=6, volume=1, buy=0, sell=1) \
        .add_entry(open=6, high=6, low=6, close=6, volume=1, buy=1, sell=0) \
        .add_entry(open=6, high=6, low=3, close=3, volume=1, buy=0, sell=1)

    fixture.frame_with_signals['COIN2/BASE'] \
        .add_entry(open=6, high=6, low=6, close=6, volume=1, buy=1, sell=0) \
        .add_entry(open=6, high=6, low=4, close=4, volume=1, buy=0, sell=1) \
        .add_entry(open=4, high=4, low=4, close=4, volume=1, buy=1, sell=0) \
        .add_entry(open=4, high=5, low=4, close=5, volume=1, buy=0, sell=1) \
        .add_entry(open=5, high=5, low=5, close=5, volume=1, buy=1, sell=0) \
        .add_entry(open=5, high=5, low=3, close=3, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.coin_res[0].market_change == 50
    assert stats.coin_res[1].market_change == -50

def test_profit():
    """Given coin trends, 'profits' should match"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=1) \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=6, low=1, close=6, volume=1, buy=0, sell=1) \
        .add_entry(open=6, high=6, low=6, close=6, volume=1, buy=1, sell=0) \
        .add_entry(open=6, high=6, low=4, close=4, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_res[0].total_profit_percentage, 88.29602988)
    assert math.isclose(stats.coin_res[0].cum_profit_percentage, 402.405)
    assert math.isclose(stats.coin_res[0].avg_profit_percentage, 134.135)

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
    assert math.isclose(stats.coin_res[0].max_realised_drawdown, -50.995)

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
    assert math.isclose(stats.coin_res[0].max_realised_drawdown, -75.4975)

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
    assert math.isclose(stats.coin_res[0].max_realised_drawdown, -68.617328354)