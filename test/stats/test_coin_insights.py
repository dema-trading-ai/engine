import math
from datetime import timedelta

from test.stats.stats_test_utils import StatsFixture
from test.utils.signal_frame import ONE_MIL


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
    assert math.isclose(stats.coin_results[0].total_profit_percentage, -1.99)


def test_return_worst_trade():
    """Given only losing trades, 'worst trade' should be worst of all trades"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE', 'COIN3/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_50_one_trade()
    fixture.frame_with_signals['COIN2/BASE'].test_scenario_down_50_one_trade()
    fixture.frame_with_signals['COIN3/BASE'].test_scenario_down_75_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_results[-1].total_profit_percentage, -75.4975)
    assert math.isclose(stats.coin_results[-1].worst_trade_ratio, 0.245025)


def test_return_best_trade():
    """Given only winning trades, 'best trade' should be best of all trades"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE', 'COIN3/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_50_one_trade()
    fixture.frame_with_signals['COIN2/BASE'].test_scenario_up_50_one_trade()
    fixture.frame_with_signals['COIN3/BASE'].test_scenario_up_100_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_results[-1].total_profit_percentage, 96.02)
    assert math.isclose(stats.coin_results[-1].best_trade_ratio, 1.9602)


def test_return_different_trades():
    """Given three different trades, should return three different trades, one per metric"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE', 'COIN3/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_50_one_trade()
    fixture.frame_with_signals['COIN2/BASE'].test_scenario_up_50_one_trade()
    fixture.frame_with_signals['COIN3/BASE'].test_scenario_up_100_one_trade()

    # Act
    stats = fixture.create().analyze()

    sorted_trades = sorted(stats.coin_results, key=lambda coin: coin.total_profit_percentage, reverse=True)

    # Assert
    assert math.isclose(sorted_trades[0].best_trade_ratio, 1.9602)
    assert math.isclose(sorted_trades[0].best_trade_currency, 32.006, abs_tol=0.001)
    assert math.isclose(sorted_trades[1].median_trade_ratio, 1.47015, abs_tol=0.00001)
    assert math.isclose(sorted_trades[1].median_trade_currency, 15.6717, abs_tol=0.0001)
    assert math.isclose(sorted_trades[2].worst_trade_ratio, 0.49005)
    assert math.isclose(sorted_trades[2].worst_trade_currency, -16.9983, abs_tol=0.0001)


def test_return_best_worst_trade_only_wins():
    """Given only winning trades, 'worst trade' should be worst of all trades,
    and 'best trade' should be best of all trades"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_50_one_trade()
    fixture.frame_with_signals['COIN2/BASE'].test_scenario_up_100_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_results[1].best_trade_ratio, 1.9602)
    assert math.isclose(stats.coin_results[1].total_profit_percentage, 96.02)
    assert math.isclose(stats.coin_results[0].worst_trade_ratio, 1.47015)
    assert math.isclose(stats.coin_results[0].total_profit_percentage, 47.015)


def test_return_best_worst_trade_only_losses():
    """Given only losing trades, 'worst trade' should be worst of all trades,
    and 'best trade' should be best of all trades"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_50_one_trade()
    fixture.frame_with_signals['COIN2/BASE'].test_scenario_down_75_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_results[0].best_trade_ratio, 0.49005, abs_tol=0.00001)
    assert math.isclose(stats.coin_results[0].total_profit_percentage, -50.995)
    assert math.isclose(stats.coin_results[1].worst_trade_ratio, 0.24502, abs_tol=0.00001)
    assert math.isclose(stats.coin_results[1].total_profit_percentage, -75.4975)


def test_return_no_trades():
    """Given no trades, profit should be zero"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_flat_no_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_results[0].total_profit_percentage, 0)
    assert math.isclose(stats.coin_results[0].cum_profit_percentage, 0)
    assert math.isclose(stats.coin_results[0].avg_profit_percentage, 0)


def test_trade_performance_return():
    # Checks the best, median, and worst trade profits, should return a float

    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_10_up_100_down_75_three_trades()

    # Act
    stats = fixture.create().analyze()

    assert math.isclose(stats.coin_results[0].best_trade_ratio, 1.9602, abs_tol=0.0001)
    assert math.isclose(stats.coin_results[0].best_trade_currency, 84.698, abs_tol=0.001)
    assert math.isclose(stats.coin_results[0].worst_trade_ratio, 0.245025, abs_tol=0.00001)
    assert math.isclose(stats.coin_results[0].worst_trade_currency, -130.541, abs_tol=0.001)
    assert math.isclose(stats.coin_results[0].median_trade_ratio, 0.88209, abs_tol=0.00001)
    assert math.isclose(stats.coin_results[0].median_trade_currency, -11.791, abs_tol=0.001)


def test_trade_performance_return_no_trades():
    # No trades, should return None

    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_down_20_down_75_no_trades()

    # Act
    stats = fixture.create().analyze()

    assert stats.coin_results[0].best_trade_ratio is None
    assert stats.coin_results[0].best_trade_currency is None
    assert stats.coin_results[0].worst_trade_ratio is None
    assert stats.coin_results[0].worst_trade_currency is None
    assert stats.coin_results[0].median_trade_ratio is None
    assert stats.coin_results[0].median_trade_currency is None


def test_nr_of_trades_no_trades():
    """Given no trades, nr of trades should be zero"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_flat_no_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_results[0].n_trades, 0)


def test_nr_of_trades_one_trade():
    """Given one trades, nr of trades should be one"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_50_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_results[0].n_trades, 1)


def test_nr_of_trades_three_trades():
    """Given one trades, nr of trades should be one"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_down_20_down_75_three_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_results[0].n_trades, 3)


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
    assert math.isclose(stats.coin_results[0].n_trades, 1)
    assert math.isclose(stats.coin_results[1].n_trades, 0)
    assert math.isclose(stats.coin_results[2].n_trades, 3)


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
    assert stats.coin_results[0].market_change == 50
    assert stats.coin_results[1].market_change == -70


def test_profit():
    """Given coin trends, 'profits' should match"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_down_75_two_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.coin_results[0].total_profit_percentage, 44.0894015)
    assert math.isclose(stats.coin_results[0].cum_profit_percentage, 69.5275)
    assert math.isclose(stats.coin_results[0].avg_profit_percentage, 34.76375)


def test_sell_reason_sell_signal():
    """ sell reason should match sell signal """
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_50_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.coin_results[0].sell_signal == 1


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
    assert stats.coin_results[0].roi == 1


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
    assert stats.coin_results[0].stoploss == 1


def test_trade_length_no_trades():
    # no trades - lengths should be 0
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_flat_no_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.coin_results[0].avg_trade_duration == timedelta(0)
    assert stats.coin_results[0].longest_trade_duration == timedelta(0)
    assert stats.coin_results[0].shortest_trade_duration == timedelta(0)


def test_trade_length_one_trade_no_close():
    # No closed trades - lengths should be 0
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_flat_one_trade_no_sell()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.coin_results[0].avg_trade_duration == timedelta(0)
    assert stats.coin_results[0].longest_trade_duration == timedelta(0)
    assert stats.coin_results[0].shortest_trade_duration == timedelta(0)


def test_trade_length_one_trade():
    # One trade, sold immediately; lengths should be 1 ms
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_flat_one_trade(timestep=ONE_MIL)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.coin_results[0].avg_trade_duration == timedelta(microseconds=1000)
    assert stats.coin_results[0].longest_trade_duration == timedelta(microseconds=1000)
    assert stats.coin_results[0].shortest_trade_duration == timedelta(microseconds=1000)


def test_trade_length_three_trades():
    # Three trades, sold immediately; lengths should be 1 ms
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_10_up_100_down_75_three_trades(timestep=ONE_MIL)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.coin_results[0].avg_trade_duration == timedelta(microseconds=1000)
    assert stats.coin_results[0].longest_trade_duration == timedelta(microseconds=1000)
    assert stats.coin_results[0].shortest_trade_duration == timedelta(microseconds=1000)


def test_trade_length_one_trade_longer():
    # One trade, sold immediately; lengths should be 3 ms
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_10_up_100_down_75_one_trade(timestep=ONE_MIL)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.coin_results[0].avg_trade_duration == timedelta(microseconds=3000)
    assert stats.coin_results[0].longest_trade_duration == timedelta(microseconds=3000)
    assert stats.coin_results[0].shortest_trade_duration == timedelta(microseconds=3000)


def test_trade_length_four_trades():
    # Three trades, sold immediately, one trade sold after 3 ms.
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_10_up_100_down_75_one_trade(timestep=ONE_MIL)
    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_down_20_down_75_three_trades(timestep=ONE_MIL)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.coin_results[0].avg_trade_duration == timedelta(microseconds=1500)
    assert stats.coin_results[0].longest_trade_duration == timedelta(microseconds=3000)
    assert stats.coin_results[0].shortest_trade_duration == timedelta(microseconds=1000)


def test_winning_weeks():
    """week is defined as winning when trade profit > market change"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_one_trade_down_20()
    fixture.frame_with_signals['COIN2/BASE'].test_scenario_down_40_one_trade_up_80()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.coin_results[0].win_weeks == 1
    assert stats.coin_results[0].loss_weeks == stats.coin_results[0].draw_weeks == 0
    assert stats.coin_results[1].loss_weeks == 1
    assert stats.coin_results[1].win_weeks == stats.coin_results[0].draw_weeks == 0
    assert stats.main_results.loss_weeks == 1
    assert stats.main_results.win_weeks == stats.main_results.draw_weeks == 0
