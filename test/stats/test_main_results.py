import math
from datetime import timedelta

from test.stats.stats_test_utils import StatsFixture, CooldownStrategy
from test.utils.signal_frame import ONE_MIL, THIRTY_MIN, EIGHT_HOURS, SIX_HOURS, TWELVE_HOURS


def test_capital():
    """Given 'value of coin rises', 'capital' should 'rise same minus fee'"""
    # Arrange
    fixture = StatsFixture(['COIN'])

    fixture.frame_with_signals['COIN'].test_scenario_up_100_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.end_capital == 196.02


def test_profit_percentage():
    """Given 'capital rises', 'profit_percentage' should 'rise accordingly'"""
    # Arrange
    fixture = StatsFixture(['COIN'])

    fixture.frame_with_signals['COIN'].test_scenario_up_100_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.overall_profit_percentage, 96.02)


def test_roi_reached_multiple_times():
    """Given 'multiple roi reached and multiple buys', 'capital' should 'reflect expected value'"""
    # Arrange
    fixture = StatsFixture(['COIN'])

    fixture.frame_with_signals['COIN'].test_scenario_up_100_one_trade_no_sell()
    fixture.frame_with_signals['COIN'].test_scenario_up_100_one_trade_no_sell()

    fixture.trading_module_config.roi = {
        "0": 10
    }

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.end_capital == 116.23211721000003


def test_roi_set_not_reached():
    """Given 'multiple roi not reached and multiple buys', 'capital' should 'reflect expected value'"""
    # Arrange
    fixture = StatsFixture(['COIN'])

    fixture.frame_with_signals['COIN'].test_scenario_up_100_one_trade()
    fixture.frame_with_signals['COIN'].test_scenario_up_100_one_trade()

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
    fixture = StatsFixture(['COIN'])

    fixture.frame_with_signals['COIN'].test_scenario_up_100_one_trade()
    fixture.frame_with_signals['COIN'].test_scenario_up_100_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.total_fee_amount, 8.821396)


def test_fee_downwards():
    """Given 'price goes down', 'fee' should 'be actual'"""
    # Arrange
    fixture = StatsFixture(['COIN'])

    fixture.frame_with_signals['COIN'].test_scenario_down_50_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.total_fee_amount, 1.495)


def test_capital_open_trade():
    """Given 'value of coin rises and open trade', 'capital' should 'rise same minus fee'"""
    # Arrange
    fixture = StatsFixture(['COIN'])

    fixture.frame_with_signals['COIN'].test_scenario_up_100_one_trade_no_sell()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.end_capital == 198.
    assert len(stats.open_trade_results) == 1


def test_stoploss():
    """Given 'value of coin falls below stoploss', 'profit' should 'lower same minus fee'"""
    # Arrange
    fixture = StatsFixture(['COIN'])

    fixture.frame_with_signals['COIN'].test_scenario_down_50_one_trade()

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
    fixture = StatsFixture(['COIN'])

    fixture.trading_module_config.stoploss_type = "trailing"

    fixture.frame_with_signals['COIN'].test_scenario_up_100_down_20_down_75_one_trade()

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
    fixture = StatsFixture(['COIN'])

    fixture.trading_module_config.stoploss_type = "dynamic"

    fixture.frame_with_signals['COIN'] \
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
    fixture = StatsFixture(['COIN'])

    fixture.trading_module_config.stoploss_type = "dynamic"

    fixture.frame_with_signals['COIN'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0, stoploss=1) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=0, stoploss=3)
    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.end_capital == 98.01


def test_dividing_assets():
    """Given 'multiple assets', '' should 'rise same minus fee'"""
    # Arrange
    fixture = StatsFixture(['COIN', 'COIN2'])

    fixture.frame_with_signals['COIN'].test_scenario_down_50_one_trade()

    fixture.frame_with_signals['COIN2'].test_scenario_down_50_one_trade()

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
    fixture = StatsFixture(['COIN', 'COIN2', 'COIN3'])

    fixture.frame_with_signals['COIN'].test_scenario_down_10_up_100_down_75_three_trades()

    fixture.frame_with_signals['COIN2'].test_scenario_up_100_down_20_down_75_three_trades()
    fixture.frame_with_signals['COIN3'].test_scenario_down_75_one_trade()

    fixture.frame_with_signals['COIN3'].test_scenario_up_50_one_trade()
    fixture.frame_with_signals['COIN3'].test_scenario_up_100_one_trade_no_sell()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.n_trades == 8
    assert stats.main_results.n_left_open_trades == 1
    assert stats.main_results.n_trades_with_loss == 5
    assert stats.main_results.n_consecutive_losses == 2


def test_n_average_trades():
    # Arrange
    fixture = StatsFixture(['COIN'])

    fixture.stats_config.backtesting_to = 86400000
    fixture.stats_config.backtesting_from = 0

    # Win/Loss/Open
    fixture.frame_with_signals['COIN'].test_scenario_down_10_up_100_down_75_three_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.n_average_trades == 3.0
    assert stats.main_results.n_left_open_trades == 0
    assert stats.main_results.n_trades_with_loss == 2
    assert stats.main_results.n_consecutive_losses == 1


def test_n_average_trades_no_trades():
    # Arrange
    fixture = StatsFixture(['COIN'])

    fixture.stats_config.backtesting_to = 86400000  # one day
    fixture.stats_config.backtesting_from = 0

    # Loss/Loss/Open
    fixture.frame_with_signals['COIN'].test_scenario_flat_no_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.n_average_trades == 0
    assert stats.main_results.n_left_open_trades == 0
    assert stats.main_results.n_trades_with_loss == 0
    assert stats.main_results.n_consecutive_losses == 0


def test_n_average_trades_more_time_less_trades():
    # Longer than a day with fewer trades following it.
    # Arrange
    fixture = StatsFixture(['COIN'])

    fixture.stats_config.backtesting_to = 172800000  # two days
    fixture.stats_config.backtesting_from = 0

    # Win/Loss/Open
    fixture.frame_with_signals['COIN'].test_scenario_down_10_up_100_down_75_three_trades()
    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.n_average_trades == 1.5


def test_n_average_trades_less_time_more_trades():
    # Half of a day with more trades.
    # Arrange
    fixture = StatsFixture(['COIN'])

    fixture.stats_config.backtesting_to = 43200000  # half a day
    fixture.stats_config.backtesting_from = 0

    # Win/Loss/Open
    fixture.frame_with_signals['COIN'].test_scenario_down_10_up_100_down_75_three_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.n_average_trades == 6.0


def test_trade_length_no_trades():
    # no trades - lengths should be 0
    # Arrange
    fixture = StatsFixture(['COIN'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN'].test_scenario_flat_no_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.avg_trade_duration == timedelta(0)
    assert stats.main_results.longest_trade_duration == timedelta(0)
    assert stats.main_results.shortest_trade_duration == timedelta(0)


def test_trade_length_one_trade_no_close():
    # No closed trades - lengths should be 0
    # Arrange
    fixture = StatsFixture(['COIN'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN'].test_scenario_flat_one_trade_no_sell()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.avg_trade_duration == timedelta(0)
    assert stats.main_results.longest_trade_duration == timedelta(0)
    assert stats.main_results.shortest_trade_duration == timedelta(0)


def test_trade_length_one_trade():
    # One trade, sold immediately; lengths should be one timestep - in this case, 30 minutes
    # Arrange
    fixture = StatsFixture(['COIN'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN'].test_scenario_flat_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.avg_trade_duration == timedelta(minutes=30)
    assert stats.main_results.longest_trade_duration == timedelta(minutes=30)
    assert stats.main_results.shortest_trade_duration == timedelta(minutes=30)


def test_trade_length_three_trades():
    # Three trades, sold immediately; lengths should be one timestep - in this case, 30 minutes
    # Arrange
    fixture = StatsFixture(['COIN'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN'].test_scenario_down_10_up_100_down_75_three_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.avg_trade_duration == timedelta(minutes=30)
    assert stats.main_results.longest_trade_duration == timedelta(minutes=30)
    assert stats.main_results.shortest_trade_duration == timedelta(minutes=30)


def test_trade_length_one_trade_longer():
    # One trade, sold immediately; lengths should be 3 ms
    # Arrange
    fixture = StatsFixture(['COIN'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN'].test_scenario_down_10_up_100_down_75_one_trade(timestep=ONE_MIL)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.avg_trade_duration == timedelta(microseconds=3000)
    assert stats.main_results.longest_trade_duration == timedelta(microseconds=3000)
    assert stats.main_results.shortest_trade_duration == timedelta(microseconds=3000)


def test_trade_length_four_trades():
    # Three trades, sold immediately, one trade sold after 3 ms.
    # Arrange
    fixture = StatsFixture(['COIN'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN'].test_scenario_down_10_up_100_down_75_one_trade(timestep=ONE_MIL)
    fixture.frame_with_signals['COIN'].test_scenario_up_100_down_20_down_75_three_trades(timestep=ONE_MIL)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.avg_trade_duration == timedelta(microseconds=1500)
    assert stats.main_results.longest_trade_duration == timedelta(microseconds=3000)
    assert stats.main_results.shortest_trade_duration == timedelta(microseconds=1000)


def test_rejected_buy_signal_no_rejection():
    # No rejected buy signal
    # Arrange
    fixture = StatsFixture(['COIN', 'COIN2', 'COIN3'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN'].test_scenario_up_100_one_trade_no_sell()
    fixture.frame_with_signals['COIN2'].test_scenario_up_100_one_trade_no_sell()
    fixture.frame_with_signals['COIN3'].test_scenario_up_100_one_trade_no_sell()

    # Act
    stats = fixture.create().analyze()

    assert stats.main_results.rejected_buy_signal == 0


def test_rejected_buy_signal_reject_max_open_trades():
    # One rejected buy signal due to max_open_trade being hit
    # Arrange
    fixture = StatsFixture(['COIN', 'COIN2', 'COIN3', 'COIN4'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN'].test_scenario_up_100_one_trade_no_sell()
    fixture.frame_with_signals['COIN2'].test_scenario_up_100_one_trade_no_sell()
    fixture.frame_with_signals['COIN3'].test_scenario_up_100_one_trade_no_sell()
    fixture.frame_with_signals['COIN4'].test_scenario_up_100_one_trade_no_sell()

    # Act
    stats = fixture.create().analyze()

    assert stats.main_results.rejected_buy_signal == 1


def test_rejected_buy_signal_reject_low_budget():
    # Three rejected buy signals due to low budget
    # Arrange
    fixture = StatsFixture(['COIN'])

    fixture.trading_module_config.starting_capital = 0

    # Win/Loss/Open
    fixture.frame_with_signals['COIN'].test_scenario_down_10_up_100_down_75_three_trades()

    # Act
    stats = fixture.create().analyze()

    assert stats.main_results.rejected_buy_signal == 3


def test_rejected_buy_signal_reject_exposure():
    # One rejected buy signal due to high exposure
    # Arrange
    fixture = StatsFixture(['COIN', 'COIN2'])

    fixture.trading_module_config.exposure_per_trade = 200

    # Win/Loss/Open
    fixture.frame_with_signals['COIN'].test_scenario_down_10_up_100_down_75_one_trade()
    fixture.frame_with_signals['COIN2'].test_scenario_down_10_up_100_down_75_one_trade()

    # Act
    stats = fixture.create().analyze()

    assert stats.main_results.rejected_buy_signal == 1


def test_sharpe_sortino_ratios_90_days():
    # Three trades per day; both ratios should return an actual value
    # Arrange
    fixture = StatsFixture(['COIN'])

    # Win/Loss/Open
    # Runs test_scenario_up_100_down_75_one_trade one per day for 90 days
    fixture.frame_with_signals['COIN'].generate_trades(days=90)

    # Act
    stats = fixture.create().analyze()

    assert math.isclose(stats.main_results.sharpe_90d, 0.1015, abs_tol=0.0001)
    assert math.isclose(stats.main_results.sortino_90d, 0.2217, abs_tol=0.0001)


def test_sharpe_sortino_ratios_3_years():
    # Three trades per day; both ratios should return an actual value
    # Arrange
    fixture = StatsFixture(['COIN'])

    # Win/Loss/Open
    # Runs test_scenario_up_100_down_75_one_trade one per day for 1095 days
    fixture.frame_with_signals['COIN'].generate_trades(days=1096)

    # Act
    stats = fixture.create().analyze()

    assert math.isclose(stats.main_results.sharpe_3y, 0.02896, abs_tol=0.00001)
    assert math.isclose(stats.main_results.sortino_3y, 0.06324, abs_tol=0.00001)


def test_sharpe_sortino_ratios_1_day():
    # Three trades, one every 30 minutes; rare instance where Sharpe is None but Sortino is a float
    # Arrange
    fixture = StatsFixture(['COIN'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN'].test_scenario_down_10_up_100_down_75_three_trades(timestep=THIRTY_MIN)

    # Act
    stats = fixture.create().analyze()

    assert stats.main_results.sharpe_90d is None
    assert math.isclose(stats.main_results.sortino_90d, -1.4142, abs_tol=0.0001)


def test_sharpe_sortino_ratios_no_sell():
    # Three trades with no selling, both ratios should return None
    # Arrange
    fixture = StatsFixture(['COIN'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN'].test_scenario_up_100_down_20_down_75_no_trades()

    # Act
    stats = fixture.create().analyze()

    assert stats.main_results.sharpe_90d is None
    assert stats.main_results.sortino_90d is None

    
def test_profitable_weeks_one_win():
    # One week, all days are positive - outcome should be one profitable week.

    # Arrange
    fixture = StatsFixture(['COIN'])

    # Win/Loss/Open
    # Start date is on a wednesday, four days makes it Sunday - one week!
    fixture.frame_with_signals['COIN'].generate_trades(days=4, timestep=EIGHT_HOURS)

    # Act
    stats = fixture.create().analyze()

    assert stats.main_results.prof_weeks_win == 1
    assert stats.main_results.prof_weeks_draw == 0
    assert stats.main_results.prof_weeks_loss == 0

    assert stats.main_results.win_weeks == 1
    assert stats.main_results.draw_weeks == 0
    assert stats.main_results.loss_weeks == 0


def test_profitable_weeks_one_loss():
    # One week, all days are negative - outcome should be one losing week.
    # Arrange
    fixture = StatsFixture(['COIN'])

    # Win/Loss/Open

    for _ in range(4):  # Start date is on a wednesday, four days makes it Sunday - one week!
        fixture.frame_with_signals['COIN'].test_scenario_down_50_one_trade(timestep=TWELVE_HOURS)

    # Act
    stats = fixture.create().analyze()

    assert stats.main_results.prof_weeks_win == 0
    assert stats.main_results.prof_weeks_draw == 0
    assert stats.main_results.prof_weeks_loss == 1

    assert stats.main_results.win_weeks == 0
    assert stats.main_results.draw_weeks == 0
    assert stats.main_results.loss_weeks == 1


def test_profitable_weeks_no_trades_market_down():
    # One week, all days are positive - outcome should be draw for profitable week, win for outperform
    # market week, since the market is going down.
    # Arrange
    fixture = StatsFixture(['COIN'])

    # Win/Loss/Open

    for _ in range(4):  # Start date is on a wednesday, four days makes it Sunday - one week!
        fixture.frame_with_signals['COIN'].test_scenario_up_100_down_20_down_75_no_trades(timestep=SIX_HOURS)

    # Act
    stats = fixture.create().analyze()

    assert stats.main_results.prof_weeks_win == 0
    assert stats.main_results.prof_weeks_draw == 1
    assert stats.main_results.prof_weeks_loss == 0

    assert stats.main_results.win_weeks == 1
    assert stats.main_results.draw_weeks == 0
    assert stats.main_results.loss_weeks == 0


def test_profitable_weeks_no_trades_market_up():
    # One week, all days are negative - outcome should be draw for profitable week, loss for outperform
    # market week, since the market is going up.
    # Arrange
    fixture = StatsFixture(['COIN'])

    # Win/Loss/Open

    for _ in range(4):  # Start date is on a wednesday, four days makes it Sunday - one week!
        fixture.frame_with_signals['COIN'].test_scenario_up_no_trades(timestep=TWELVE_HOURS)

    # Act
    stats = fixture.create().analyze()

    assert stats.main_results.prof_weeks_win == 0
    assert stats.main_results.prof_weeks_draw == 1
    assert stats.main_results.prof_weeks_loss == 0

    assert stats.main_results.win_weeks == 0
    assert stats.main_results.draw_weeks == 0
    assert stats.main_results.loss_weeks == 1


def test_profitable_weeks_no_trades_market_flat():
    # One week, all days are flat - outcome should be drawn for profitable week, draw for outperform
    # market week, since the market is flat.

    # Arrange
    fixture = StatsFixture(['COIN'])

    # Win/Loss/Open
    for _ in range(4):  # Start date is on a wednesday, four days makes it Sunday - one week!
        fixture.frame_with_signals['COIN'].test_scenario_flat_no_trades(timestep=TWELVE_HOURS)

    # Act
    stats = fixture.create().analyze()

    assert stats.main_results.prof_weeks_win == 0
    assert stats.main_results.prof_weeks_draw == 1
    assert stats.main_results.prof_weeks_loss == 0

    assert stats.main_results.win_weeks == 0
    assert stats.main_results.draw_weeks == 1
    assert stats.main_results.loss_weeks == 0


def test_risk_reward_ratio():
    # Checks that two trades return a ratio, should return a float

    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_down_75_two_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.risk_reward_ratio, 1.849, abs_tol=0.001)


def test_risk_reward_ratio_no_trade():
    # Checks that the risk/ reward ratio can't be computed as there are no trades, should return 0 as an int

    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_no_trades()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.risk_reward_ratio == 0
    assert isinstance(stats.main_results.risk_reward_ratio, int)


def test_risk_reward_ratio_one_winning_trade():
    # Checks that the risk/ reward ratio can't be computed as there are no losing trades, should return 0.0 as a float

    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_50_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.risk_reward_ratio == 0
    assert isinstance(stats.main_results.risk_reward_ratio, float)


def test_risk_reward_ratio_one_losing_trade():
    # Checks that the risk/ reward ratio can't be computed as there are no winning trades, should return 0.0 as a float

    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_50_one_trade()

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.risk_reward_ratio == 0
    assert isinstance(stats.main_results.risk_reward_ratio, float)


def test_cooldown_sell_signal():
    # Tests the cooldown function - with multiple buy and sell signals, on which the consecutive ones fall in
    # the cooldown period.

    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_10_up_100_down_75_three_trades()

    # Act
    stats = fixture.create_with_strategy(CooldownStrategy()).analyze()

    # Assert
    assert stats.main_results.n_trades == 1


def test_cooldown_stoploss():
    # Tests the cooldown function - when stoploss is hit

    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.trading_module_config.stoploss = -25
    fixture.stats_config.stoploss = -25

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_down_50_one_trade()
    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_50_one_trade()
    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_50_one_trade()

    # Act
    stats = fixture.create_with_strategy(CooldownStrategy()).analyze()

    # Assert
    assert stats.main_results.n_trades == 2


def test_cooldown_roi():
    # Tests the cooldown function - when roi is hit

    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.trading_module_config.roi = {
        "0": 25
    }

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_50_one_trade()
    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_50_one_trade()
    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_50_one_trade()
    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_50_one_trade()
    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_50_one_trade()

    # Act
    stats = fixture.create_with_strategy(CooldownStrategy()).analyze()

    # Assert
    assert stats.main_results.n_trades == 3
