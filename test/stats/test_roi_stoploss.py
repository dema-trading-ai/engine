from test.stats.stats_test_utils import StatsFixture


def test_roi():
    """given `value of coin rises over ROI limit` should sell at ROI price"""
    # arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=0) \
        .add_entry(open=2, high=3, low=2, close=2, volume=1, buy=0, sell=0)

    fixture.trading_module_config.roi = {
        "0": 150
    }

    # act
    stats = fixture.create().analyze()

    # assert
    assert stats.main_results.end_capital == 245.025


def test_both_roi_stoploss():
    """given 'both ROI and stoploss triggered single OHLCV candle' should 'close trade for open price'"""
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
    assert stats.main_results.end_capital == 98.01
