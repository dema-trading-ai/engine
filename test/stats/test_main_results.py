import math
from datetime import timedelta

from test.stats.stats_test_utils import StatsFixture
from test.utils.signal_frame import ONE_MIL, THIRTY_MIN


def test_capital():
    """Given 'value of coin rises', 'capital' should 'rise same minus fee'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.end_capital == 196.02


def test_profit_percentage():
    """Given 'capital rises', 'profit_percentage' should 'rise accordingly'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.overall_profit_percentage, 96.02)


def test_roi_reached_multiple_times():
    """Given 'multiple roi reached and multiple buys', 'capital' should 'reflect expected value'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_one_trade_no_sell()
    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_one_trade_no_sell()

    fixture.trading_module_config.roi = {
        "0": 10
    }

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.end_capital == 116.23211721000003


def test_roi_set_not_reached():
    """Given 'multiple roi reached and multiple buys', 'capital' should 'reflect expected value'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_one_trade()
    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_one_trade()

    fixture.trading_module_config.roi = {
        "0": 150
    }

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.end_capital, 384.238404)


def test_fee():
    """Given 'multiple trades', 'fee' should 'be actual'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_one_trade()
    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.total_fee_amount, 8.821396)


def test_fee_downwards():
    """Given 'price goes down', 'fee' should 'be actual'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_50_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.total_fee_amount, 1.495)


def test_capital_open_trade():
    """Given 'value of coin rises and open trade', 'capital' should 'rise same minus fee'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_one_trade_no_sell()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.end_capital == 198.
    assert len(stats.open_trade_results) == 1


def test_stoploss():
    """Given 'value of coin falls below stoploss', 'profit' should 'lower same minus fee'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_50_one_trade()

    fixture.trading_module_config.stoploss = -25
    fixture.stats_config.stoploss = -25

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.end_capital == 74.25


def test_trailing_stoploss():
    """Given 'trailing stoploss and value first rises and then
    dips below stoploss', 'end capital' should 'represent sold
    on stoploss price'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.trading_module_config.stoploss_type = "trailing"

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_down_20_down_75_one_trade()

    fixture.trading_module_config.stoploss = -25
    fixture.stats_config.stoploss = -25

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.end_capital == 147.015


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

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_50_one_trade()

    fixture.frame_with_signals['COIN2/BASE'].test_scenario_down_50_one_trade()

    fixture.trading_module_config.stoploss = 25
    fixture.stats_config.stoploss = 25

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.end_capital == 74.25


def test_n_trades():
    """Given 'trades were made',
    'number of trades' should 'display correct amount' """
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE', 'COIN3/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_10_up_100_down_75_three_trades()

    fixture.frame_with_signals['COIN2/BASE'].test_scenario_up_100_down_20_down_75_three_trades()
    fixture.frame_with_signals['COIN3/BASE'].test_scenario_down_75_one_trade()

    fixture.frame_with_signals['COIN3/BASE'].test_scenario_up_50_one_trade()
    fixture.frame_with_signals['COIN3/BASE'].test_scenario_up_100_one_trade_no_sell()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.n_trades == 9
    assert stats.main_results.n_left_open_trades == 1
    assert stats.main_results.n_trades_with_loss == 5
    assert stats.main_results.n_consecutive_losses == 2


def test_n_average_trades():
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.stats_config.backtesting_to = 86400000
    fixture.stats_config.backtesting_from = 0

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_10_up_100_down_75_three_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.n_average_trades == 3.0
    assert stats.main_results.n_left_open_trades == 0
    assert stats.main_results.n_trades_with_loss == 2
    assert stats.main_results.n_consecutive_losses == 1


def test_n_average_trades_no_trades():
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.stats_config.backtesting_to = 86400000  # one day
    fixture.stats_config.backtesting_from = 0

    # Loss/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_flat_no_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.n_average_trades == 0
    assert stats.main_results.n_left_open_trades == 0
    assert stats.main_results.n_trades_with_loss == 0
    assert stats.main_results.n_consecutive_losses == 0


def test_n_average_trades_more_time_less_trades():
    # Longer than a day with less trades following it.
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.stats_config.backtesting_to = 172800000  # two days
    fixture.stats_config.backtesting_from = 0

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_10_up_100_down_75_three_trades()
    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.n_average_trades == 1.5


def test_n_average_trades_less_time_more_trades():
    # Half of a day with more trades.
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.stats_config.backtesting_to = 43200000  # half a day
    fixture.stats_config.backtesting_from = 0

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_10_up_100_down_75_three_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.n_average_trades == 6.0


def test_trade_length_no_trades():
    # no trades - lengths should be 0
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_flat_no_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.avg_trade_duration == timedelta(0)
    assert stats.main_results.longest_trade_duration == timedelta(0)
    assert stats.main_results.shortest_trade_duration == timedelta(0)


def test_trade_length_one_trade_no_close():
    # No closed trades - lengths should be 0
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_flat_one_trade_no_sell()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.avg_trade_duration == timedelta(0)
    assert stats.main_results.longest_trade_duration == timedelta(0)
    assert stats.main_results.shortest_trade_duration == timedelta(0)


def test_trade_length_one_trade():
    # One trade, sold immediately; lengths should be 1 day
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_flat_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.avg_trade_duration == timedelta(days=1)
    assert stats.main_results.longest_trade_duration == timedelta(days=1)
    assert stats.main_results.shortest_trade_duration == timedelta(days=1)


def test_trade_length_three_trades():
    # Three trades, sold immediately; lengths should be 1 day
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_10_up_100_down_75_three_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.avg_trade_duration == timedelta(days=1)
    assert stats.main_results.longest_trade_duration == timedelta(days=1)
    assert stats.main_results.shortest_trade_duration == timedelta(days=1)


def test_trade_length_one_trade_longer():
    # One trade, sold immediately; lengths should be 3 ms
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_10_up_100_down_75_one_trade(timestep=ONE_MIL)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.avg_trade_duration == timedelta(microseconds=3000)
    assert stats.main_results.longest_trade_duration == timedelta(microseconds=3000)
    assert stats.main_results.shortest_trade_duration == timedelta(microseconds=3000)


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
    assert stats.main_results.avg_trade_duration == timedelta(microseconds=1500)
    assert stats.main_results.longest_trade_duration == timedelta(microseconds=3000)
    assert stats.main_results.shortest_trade_duration == timedelta(microseconds=1000)


def test_rejected_buy_signal_no_rejection():
    # No rejected buy signal
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE', 'COIN3/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_one_trade_no_sell()
    fixture.frame_with_signals['COIN2/BASE'].test_scenario_up_100_one_trade_no_sell()
    fixture.frame_with_signals['COIN3/BASE'].test_scenario_up_100_one_trade_no_sell()

    # Act
    stats = fixture.create().analyze()

    assert stats.main_results.rejected_buy_signal == 0


def test_rejected_buy_signal_reject_max_open_trades():
    # One rejected buy signal due to max_open_trade being hit
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE', 'COIN3/BASE', 'COIN4/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_one_trade_no_sell()
    fixture.frame_with_signals['COIN2/BASE'].test_scenario_up_100_one_trade_no_sell()
    fixture.frame_with_signals['COIN3/BASE'].test_scenario_up_100_one_trade_no_sell()
    fixture.frame_with_signals['COIN4/BASE'].test_scenario_up_100_one_trade_no_sell()

    # Act
    stats = fixture.create().analyze()

    assert stats.main_results.rejected_buy_signal == 1


def test_rejected_buy_signal_reject_low_budget():
    # Three rejected buy signals due to low budget
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.trading_module_config.starting_capital = 0

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_10_up_100_down_75_three_trades()

    # Act
    stats = fixture.create().analyze()

    assert stats.main_results.rejected_buy_signal == 3


def test_rejected_buy_signal_reject_exposure():
    # One rejected buy signal due to high exposure
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE'])

    fixture.trading_module_config.exposure_per_trade = 200

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_10_up_100_down_75_one_trade()
    fixture.frame_with_signals['COIN2/BASE'].test_scenario_down_10_up_100_down_75_one_trade()

    # Act
    stats = fixture.create().analyze()

    assert stats.main_results.rejected_buy_signal == 1


def test_ratios_90_days():
    # Three trades, one per day; both ratios should return an actual value
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].generate_trades(days=90)  # Runs test_scenario_up_100_down_75_one_trade one per day for 90 days

    # Act
    stats = fixture.create().analyze()

    assert math.isclose(stats.main_results.sharpe_90d, 0.1015, abs_tol=0.0001)
    assert math.isclose(stats.main_results.sortino_90d, 0.2217, abs_tol=0.0001)


def test_ratios_3_years():
    # Three trades, one per day; both ratios should return an actual value
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].generate_trades(days=1095)  # Runs test_scenario_up_100_down_75_one_trade one per day for 1095 days

    # Act
    stats = fixture.create().analyze()

    assert math.isclose(stats.main_results.sharpe_3y, 0.02896, abs_tol=0.00001)
    assert math.isclose(stats.main_results.sortino_3y, 0.06324, abs_tol=0.00001)


def test_ratios_1_day():
    # Three trades, one every 30 minutes; both ratios should return None
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_10_up_100_down_75_three_trades(timestep=THIRTY_MIN)

    # Act
    stats = fixture.create().analyze()

    assert stats.main_results.sharpe_90d is None
    assert stats.main_results.sharpe_3y is None


def test_ratios_no_sell():
    # Three trades with no selling, both rations both ratios should return None
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_down_20_down_75_no_trades()

    # Act
    stats = fixture.create().analyze()

    assert stats.main_results.sharpe_90d is None
    assert stats.main_results.sortino_90d is None
