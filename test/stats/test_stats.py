import math
from test.stats.stats_test_utils import StatsFixture
from test.utils.signal_frame import TradeAction
from utils import get_ohlcv_indicators


def test_capital():
    """Given 'value of coin rises', 'capital' should 'rise same minus fee'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.end_capital == 196.02


def test_profit_percentage():
    """Given 'capital rises', 'profit_percentage' should 'rise accordingly'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.overall_profit_percentage, 96.02)


def test_roi_reached_multiple_times():
    """Given 'multiple roi reached and multiple buys', 'capital' should 'reflect expected value'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE']\
        .multiply_price(2, TradeAction.BUY)\
        .multiply_price(2)\
        .multiply_price(2, TradeAction.BUY) \
        .multiply_price(2)

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

    fixture.frame_with_signals['COIN/BASE'] \
        .multiply_price(2, TradeAction.BUY) \
        .multiply_price(2, TradeAction.SELL) \
        .multiply_price(2, TradeAction.BUY) \
        .multiply_price(2, TradeAction.SELL)

    fixture.trading_module_config.roi = {
        "0": 1.5 * 100
    }

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.end_capital, 384.238404)


def test_fee():
    """Given 'multiple trades', 'fee' should 'be actual'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .multiply_price(1, TradeAction.BUY)\
        .multiply_price(2, TradeAction.SELL) \
        .multiply_price(1, TradeAction.BUY) \
        .multiply_price(2, TradeAction.SELL)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.total_fee_amount, 8.821396)


def test_fee_downwards():
    """Given 'price goes down', 'fee' should 'be actual'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .multiply_price(1, TradeAction.BUY)\
        .multiply_price(0.5, TradeAction.SELL) \

    fixture.trading_module_config.roi = {
        "0": 100
    }
    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.total_fee_amount, 1.495)


def test_capital_open_trade():
    """Given 'value of coin rises and open trade', 'capital' should 'rise same minus fee'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=0)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.end_capital == 198.
    assert len(stats.open_trade_res) == 1


def test_stoploss():
    """Given 'value of coin falls below stoploss', 'profit' should 'lower same minus fee'"""
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
    assert stats.main_results.end_capital == 73.5075


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

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=0)

    fixture.frame_with_signals['COIN2/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=0)

    fixture.trading_module_config.stoploss = 25
    fixture.stats_config.stoploss = 25

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.end_capital == 73.5075


def test_simple_realized_drawdown():
    """Given 'sell at half value', 'realized drawdown' should 'be half'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=1)
    
    fixture.frame_with_signals['COIN2/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1.5, close=1.5, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, -38.74375)

def test_simple_no_realized_drawdown():
    """Given 'sell at half value', 'realized drawdown' should 'be half'"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=1)
    
    fixture.frame_with_signals['COIN2/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, 0)


def test_two_periods_realized_drawdown_v1():
    """Given multiple trades, creating two separate drawdown
    periods, realized drawdown should be the drawdown of the biggest drawdown
    period"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1.5, close=1.5, volume=1, buy=0, sell=1) \
        .add_entry(open=1.5, high=1.5, low=1.5, close=1.5, volume=1, buy=1, sell=0) \
        .add_entry(open=1.5, high=6, low=1.5, close=6, volume=1, buy=0, sell=1) \
        .add_entry(open=6, high=6, low=6, close=6, volume=1, buy=1, sell=0) \
        .add_entry(open=6, high=6, low=3, close=3, volume=1, buy=0, sell=1) \
        .add_entry(open=3, high=3, low=3, close=3, volume=1, buy=1, sell=0) \
        .add_entry(open=3, high=4, low=3, close=4, volume=1, buy=0, sell=1)

    fixture.frame_with_signals['COIN2/BASE'] \
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
    assert math.isclose(stats.main_results.max_realised_drawdown, -50.995)

def test_two_periods_realized_drawdown_v2():
    """Given multiple trades, creating two separate drawdown
    periods, realized drawdown should be the drawdown of the biggest drawdown
    period"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=4, high=4, low=4, close=4, volume=1, buy=1, sell=0) \
        .add_entry(open=4, high=4, low=1, close=1, volume=1, buy=0, sell=1) \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=5, low=1, close=5, volume=1, buy=0, sell=1) \
        .add_entry(open=5, high=5, low=5, close=5, volume=1, buy=1, sell=0) \
        .add_entry(open=5, high=5, low=3, close=3, volume=1, buy=0, sell=1) \
        .add_entry(open=3, high=3, low=3, close=3, volume=1, buy=1, sell=0) \
        .add_entry(open=3, high=6, low=3, close=6, volume=1, buy=0, sell=1)

    fixture.frame_with_signals['COIN2/BASE'] \
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
    assert math.isclose(stats.main_results.max_realised_drawdown, -75.4975)

def test_two_periods_realized_drawdown_v3():
    """Given multiple trades, creating one drawdown period, realized
    drawdown should be the drawdown of the entire period"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=6, high=6, low=6, close=6, volume=1, buy=1, sell=0) \
        .add_entry(open=6, high=6, low=4, close=4, volume=1, buy=0, sell=1) \
        .add_entry(open=4, high=4, low=4, close=4, volume=1, buy=1, sell=0) \
        .add_entry(open=4, high=5, low=4, close=5, volume=1, buy=0, sell=1) \
        .add_entry(open=5, high=5, low=5, close=5, volume=1, buy=1, sell=0) \
        .add_entry(open=5, high=5, low=2, close=2, volume=1, buy=0, sell=1) \

    fixture.frame_with_signals['COIN2/BASE'] \
        .add_entry(open=6, high=6, low=6, close=6, volume=1, buy=1, sell=0) \
        .add_entry(open=6, high=6, low=4, close=4, volume=1, buy=0, sell=1) \
        .add_entry(open=4, high=4, low=4, close=4, volume=1, buy=1, sell=0) \
        .add_entry(open=4, high=5, low=4, close=5, volume=1, buy=0, sell=1) \
        .add_entry(open=5, high=5, low=5, close=5, volume=1, buy=1, sell=0) \
        .add_entry(open=5, high=5, low=2, close=2, volume=1, buy=0, sell=1) \

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_realised_drawdown, -68.617328354)


def test_n_trades():
    """Given 'trades where made', 
    'number of trades' should 'display correct amount' """
    # Arrange
    fixture = StatsFixture(['COIN/BASE', 'COIN2/BASE', 'COIN3/BASE'])

    # Win/Loss/Open
    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=1) \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=1) \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0)

    # Win/Win/Open
    fixture.frame_with_signals['COIN2/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=1) \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=3, low=2, close=3, volume=1, buy=0, sell=1) \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0)

    # Loss/Loss/Open
    fixture.frame_with_signals['COIN3/BASE'] \
        .add_entry(open=3, high=3, low=3, close=3, volume=1, buy=1, sell=0) \
        .add_entry(open=3, high=3, low=2, close=2, volume=1, buy=0, sell=1) \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=1) \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert stats.main_results.n_trades == 9
    assert stats.main_results.n_left_open_trades == 3
    assert stats.main_results.n_trades_with_loss == 3
    assert stats.main_results.n_consecutive_losses == 2


def test_positive_best_worst_trade():
    """Given one positive trade, 'best trade' should be trade profit,
    worst trade should be 0"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_win_single_trade, 96.02)
    assert math.isclose(stats.main_results.max_drawdown_single_trade, 0)


def test_negative_best_worst_trade():
    """Given one negative trade, 'worst trade' should be trade profit,
    best trade should be 0"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_win_single_trade, 0)
    assert math.isclose(stats.main_results.max_drawdown_single_trade, -50.995)


def test_best_worst_trade():
    """Given one negative trade, and one positive trade, 'worst trade' should be drawdown
    of negative trade, 'best trade' should be profit of positive trade"""
    # Arrange
    fixture = StatsFixture(['COIN/BASE'])

    fixture.frame_with_signals['COIN/BASE'] \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=1) \
        .add_entry(open=2, high=2, low=1, close=1, volume=1, buy=1, sell=0) \
        .add_entry(open=2, high=2, low=2, close=2, volume=1, buy=0, sell=1)

    # Act
    stats = fixture.create().analyze()

    # Assert
    assert math.isclose(stats.main_results.max_win_single_trade, 96.02)
    assert math.isclose(stats.main_results.max_drawdown_single_trade, -50.995)




