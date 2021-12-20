from datetime import timedelta

from test.stats.stats_test_utils import StatsFixture


def test_roi():
    """given `value of coin rises over ROI limit` should sell at ROI price"""
    # arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_one_trade_no_sell()

    fixture.trading_module_config.roi = {
        "0": 75
    }

    # act
    stats = fixture.create().analyze()

    # assert
    assert stats.main_results.end_capital == 171.5175


def test_stoploss():
    """Given 'value of coin falls below stoploss', 'profit' should be 'stoploss minus fee'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=1)

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

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=0, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=0) \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=0, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=0) \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=0, sell=0)

    fixture.trading_module_config.stoploss = -25
    fixture.stats_config.stoploss = -25

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.trades[0].closed_at - stats.trades[0].opened_at == timedelta(days=4)
    assert stats.main_results.end_capital == 147.015


def test_trailing_stoploss_multiple_dips():
    """Given 'trailing stoploss and value first rises and then
    dips below stoploss', 'end capital' should 'represent sold
    on stoploss price'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.trading_module_config.stoploss_type = "trailing"

    fixture.frame_with_signals['COIN/BASE'].test_scenario_up_100_down_20_down_75_one_trade_long_timesteps()

    fixture.trading_module_config.stoploss = -25
    fixture.stats_config.stoploss = -25

    # Act
    stats = fixture.create().analyze()

    # Assert
    # assert stats.trades[0].closed_at == datetime.fromtimestamp(5/1000)
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


def test_both_roi_stoploss():
    """given 'both ROI and stoploss triggered single OHLCV candle' 
    should 'close trade for open price' """
    # arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=0.1, close=2, volume=1, buy=0, sell=0)

    fixture.trading_module_config.roi = {
        "0": 50
    }

    fixture.trading_module_config.stoploss = -50
    fixture.stats_config.stoploss = -50

    # act
    stats = fixture.create().analyze()

    # assert
    assert stats.main_results.end_capital == 100
