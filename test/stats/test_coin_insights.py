import math

from modules.stats.trade import SellReason
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


def test_profit_worst_trade():
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


def test_profit_best_trade():
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


def test_profit_best_worst_trade_only_wins():
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
    assert math.isclose(stats.coin_res[1].total_profit_percentage, 96.02)
    assert math.isclose(stats.main_results.worst_trade_profit_percentage, 47.015)
    assert math.isclose(stats.coin_res[0].total_profit_percentage, 47.015)


def test_profit_best_worst_trade_only_losses():
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
    assert math.isclose(stats.coin_res[0].total_profit_percentage, -50.995)
    assert math.isclose(stats.main_results.worst_trade_profit_percentage, -75.4975)
    assert math.isclose(stats.coin_res[1].total_profit_percentage, -75.4975)


def test_profit_no_trades():
    """Given no trades, profit should be zero"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_flat_no_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.best_trade_profit_percentage, 0)
    assert math.isclose(stats.main_results.worst_trade_profit_percentage, 0)
    assert math.isclose(stats.coin_res[0].total_profit_percentage, 0)
    assert math.isclose(stats.coin_res[0].cum_profit_percentage, 0)
    assert math.isclose(stats.coin_res[0].avg_profit_percentage, 0)


def test_nr_of_trades_no_trades():
    """Given no trades, nr of trades should be zero"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_flat_no_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_res[0].n_trades, 0)


def test_nr_of_trades_one_trade():
    """Given one trades, nr of trades should be one"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_50_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_res[0].n_trades, 1)


def test_nr_of_trades_three_trades():
    """Given one trades, nr of trades should be one"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_20_down_75_three_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_res[0].n_trades, 3)


def test_nr_of_trades_three_coins():
    """Given multiple coins, nr of trades should be correct"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE', 'COIN3/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_50_one_trade()
    fixture.frame_with_signals['COIN/BASE'].test_scenario_flat_no_trades()
    fixture.frame_with_signals['COIN/BASE'].test_scenario_flat_no_trades()

    fixture.frame_with_signals['COIN2/BASE'].test_scenario_flat_no_trades()
    fixture.frame_with_signals['COIN2/BASE'].test_scenario_flat_no_trades()
    fixture.frame_with_signals['COIN2/BASE'].test_scenario_flat_no_trades()

    fixture.frame_with_signals['COIN3/BASE'].test_scenario_down_10_up_100_down_75_three_trades()

    # Act
    stats = fixture.create().analyze()


    # Assert
    assert math.isclose(stats.coin_res[0].n_trades, 1)
    assert math.isclose(stats.coin_res[1].n_trades, 0)
    assert math.isclose(stats.coin_res[2].n_trades, 3)


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


def test_sell_reason_sell_signal():
    """ sell reason should match sell signal """
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_50_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.coin_res[0].sell_signal == 1


def test_sell_reason_roi():
    """ sell reason should match sell signal """
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_one_trade()

    fixture.trading_module_config.roi = {
        "0": 50
    }

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.coin_res[0].roi == 1


def test_sell_reason_stoploss():
    """ sell reason should match sell signal """
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_50_one_trade()
    
    fixture.trading_module_config.stoploss = -25
    fixture.stats_config.stoploss = -25

    # Act
    stats = fixture.create().analyze()
    
    # Assert
    assert stats.coin_res[0].stoploss == 1


def test_drawdown_equality():
    """Given one coin, 'max seen/real drawdown' from main results should be equal
    to that of the coin insights"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_20_down_75_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.max_seen_drawdown == \
        stats.coin_res[0].max_seen_drawdown
    assert stats.main_results.max_realised_drawdown == \
        stats.coin_res[0].max_realised_drawdown


def test_seen_drawdown_equals_realised_drawdown():
    """Given one coin, 'max seen drawdown' should be the 
    lowest seen drawdown and 'max realised drawdown' should be the lowest
    actual realised drawdown"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_50_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.coin_res[0].max_seen_drawdown == \
        stats.coin_res[0].max_realised_drawdown


def test_drawdown_simple():
    """Given one coin, 'max seen drawdown' should be the 
    lowest seen drawdown and 'max realised drawdown' should be the lowest
    actual realised drawdown"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_20_down_75_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_res[0].max_seen_drawdown, -80.2)
    assert math.isclose(stats.coin_res[0].max_realised_drawdown, -60.796)


def test_drawdown_multiple_trades():
    """Given multiple trades, 'max seen drawdown' should be the lowest seen drawdown
    of the combined trades"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_10_up_100_down_75_three_trades()
    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_20_down_75_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_res[0].max_seen_drawdown, -95.148505)
    assert math.isclose(stats.coin_res[0].max_realised_drawdown, -90.3940399)


def test_drawdown_multiple_pairs():
    """Given multiple pairs, 'max seen drawdown' should be the lowest seen drawdown
    of the different pairs combined"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_10_up_100_down_75_three_trades()
    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_20_down_75_one_trade()

    fixture.frame_with_signals['COIN2/BASE'].test_scenario_up_100_20_down_75_three_trades()
    fixture.frame_with_signals['COIN2/BASE'].test_scenario_down_10_up_100_down_75_three_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_res[0].max_seen_drawdown, -95.148505)
    assert math.isclose(stats.coin_res[0].max_realised_drawdown, -90.3940399)

    assert math.isclose(stats.coin_res[1].max_seen_drawdown, -83.22282373767418)
    assert math.isclose(stats.coin_res[1].max_realised_drawdown, -83.05335731078199)

    assert math.isclose(stats.main_results.max_seen_drawdown, -84.49838188862499)
    assert math.isclose(stats.main_results.max_realised_drawdown, -85.52890115608895)
