import math
from test.stats.stats_test_utils import StatsFixture


def test_fee_equals_stoploss():
    """Opening trade and fee is equal to stoploss, 
    'worst trade profit percentage' should be equal to 2x fee"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_flat_one_trade_no_sell()

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

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_50_one_trade()
    fixture.frame_with_signals['COIN2/BASE'].test_scenario_down_50_one_trade()
    fixture.frame_with_signals['COIN3/BASE'].test_scenario_down_75_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_res[-1].total_profit_percentage, -75.4975)
    assert math.isclose(stats.main_results.worst_trade_profit_percentage, -75.4975)


def test_best_trade():
    """Given only winning trades, 'best trade' should be best of all trades"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE', 'COIN3/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_50_one_trade()
    fixture.frame_with_signals['COIN2/BASE'].test_scenario_up_50_one_trade()
    fixture.frame_with_signals['COIN3/BASE'].test_scenario_up_100_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_res[-1].total_profit_percentage, 96.02)
    assert math.isclose(stats.main_results.best_trade_profit_percentage, 96.02)


def test_best_worst_trade_only_wins():
    """Given only winning trades, 'worst trade' should be worst of all trades,
    and 'best trade' should be best of all trades"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_50_one_trade()
    fixture.frame_with_signals['COIN2/BASE'].test_scenario_up_100_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.best_trade_profit_percentage, 96.02)
    assert math.isclose(stats.main_results.worst_trade_profit_percentage, 47.015)


def test_best_worst_trade_only_losses():
    """Given only losing trades, 'worst trade' should be worst of all trades,
    and 'best trade' should be best of all trades"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_50_one_trade()
    fixture.frame_with_signals['COIN2/BASE'].test_scenario_down_75_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.best_trade_profit_percentage, -50.995)
    assert math.isclose(stats.main_results.worst_trade_profit_percentage, -75.4975)


def test_marketchange():
    """Given coins with upward and downward trends, 'market change' should be 
    change between close value of first and last tick"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_down_75_one_trade()
    fixture.frame_with_signals['COIN2/BASE'].test_scenario_down_80_up_50_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.coin_res[0].market_change == 50
    assert stats.coin_res[1].market_change == -70


def test_profit():
    """Given coin trends, 'profits' should match"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_down_75_two_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_res[0].total_profit_percentage, 44.0894015)
    assert math.isclose(stats.coin_res[0].cum_profit_percentage, 69.5275)
    assert math.isclose(stats.coin_res[0].avg_profit_percentage, 34.76375)
