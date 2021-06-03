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


def test_open_trades_profit_percentage_positive():
    """Given a profiting left open trade, profit percentage should be correct, including buy fee"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=0)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.open_trade_res[0].curr_profit_percentage == 98


def test_open_trades_profit_percentage_negative():
    """Given a losing left open trade, profit percentage should be correct, including buy fee"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=0)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.open_trade_res[0].curr_profit_percentage == -50.5


def test_open_trades_profit_positive():
    """Given a profiting left open trade, profit should be correct, including buy fee"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=0)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.open_trade_res[0].curr_profit == 98


def test_open_trades_profit_negative():
    """Given a losing left open trade, profit should be correct, including buy fee"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=0)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.open_trade_res[0].curr_profit == -50.5
