from test.stats.stats_test_utils import StatsFixture


def test_open_trades_pair():
    """Given a left open trade, pair should match the coin pair"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=0)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.open_trade_res[0].pair == 'COIN/BASE'
