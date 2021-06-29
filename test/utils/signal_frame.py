from enum import Enum
from typing import TypeVar


class TradeAction(Enum):
    BUY = 1
    SELL = 2
    NOTHING = 3


class MockOHLCVWithSignal(dict, object):
    __key: object
    current_time: int

    def __init__(self, key):
        super().__init__()
        self.__key = key
        self.current_time = 0

    def add_entry(self, open=1., high=1., low=1., close=1., volume=1., buy=0, sell=0, stoploss=0):
        self.current_time += 1
        self.update({self.current_time: {'time': self.current_time,
                                         'open': open,
                                         'high': high,
                                         'low': low,
                                         'close': close,
                                         'volume': volume,
                                         'pair': self.__key,
                                         'buy': buy,
                                         'sell': sell,
                                         'stoploss': stoploss
                                         }})
        return self

    def test_scenario_flat_no_trades(self):
        """
        Chart flow:
        1. Trend stays the same
        """
        self.add_entry(open=2, high=2, low=2, close=2, volume=1, buy=0, sell=0)
        self.add_entry(open=2, high=2, low=2, close=2, volume=1, buy=0, sell=0)

    def test_scenario_flat_one_trade(self):
        """
        Chart flow:
        1. Trend stays the same
        """
        self.add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0)
        self.add_entry(open=2, high=2, low=2, close=2, volume=1, buy=0, sell=1)

    def test_scenario_flat_one_trade_no_sell(self):
        """
        Chart flow:
        1. Trend stays the same (but no sell signal)
        """
        self.add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0)
        self.add_entry(open=2, high=2, low=2, close=2, volume=1, buy=0, sell=0)

    def test_scenario_down_50_one_trade(self):
        """
        Chart flow:
        1. Trend goes down 50%
        """
        self.add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0)
        self.add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=1)

    def test_scenario_down_50_one_trade_no_sell(self):
        """
        Chart flow:
        1. Trend goes down 50%
        """
        self.add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0)
        self.add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=0)

    def test_scenario_down_75_one_trade(self):
        """
        Chart flow:
        1. Trend goes down 75%
        """
        self.add_entry(open=4, high=4, low=4, close=4, volume=1, buy=1, sell=0)
        self.add_entry(open=4, high=4, low=1, close=1, volume=1, buy=0, sell=1)

    def test_scenario_up_50_one_trade(self):
        """
        Chart flow:
        1. Trend goes up 50%
        """
        self.add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0)
        self.add_entry(open=2, high=3, low=2, close=3, volume=1, buy=0, sell=1)

    def test_scenario_up_100_one_trade(self):
        """
        Chart flow:
        1. Trend goes up 100%
        """
        self.add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0)
        self.add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=1)

    def test_scenario_up_100_one_trade_no_sell(self):
        """
        Chart flow:
        1. Trend goes up 100%
        """
        self.add_entry(open=1, high=1, low=1, close=1, volume=1, buy=1, sell=0)
        self.add_entry(open=1, high=2, low=1, close=2, volume=1, buy=0, sell=0)

    def test_scenario_up_100_down_50_one_trade(self):
        """
        Chart flow:
        1. Trend goes up 100%
        2. Trend goes down 50%
        """
        self.add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0)
        self.add_entry(open=2, high=4, low=2, close=4, volume=1, buy=0, sell=0)
        self.add_entry(open=4, high=4, low=2, close=2, volume=1, buy=0, sell=1)

    def test_scenario_up_100_down_75_one_trade(self):
        """
        Chart flow:
        1. Trend goes up 100%
        2. Trend goes down 75%
        """
        self.add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0)
        self.add_entry(open=2, high=4, low=2, close=4, volume=1, buy=0, sell=0)
        self.add_entry(open=4, high=4, low=3, close=3, volume=1, buy=0, sell=1)

    def test_scenario_up_100_down_75_two_trades(self):
        """
        Chart flow:
        1. Trend goes up 100%
        2. Trend goes down 75%
        """
        self.add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0)
        self.add_entry(open=2, high=4, low=2, close=4, volume=1, buy=0, sell=1)
        self.add_entry(open=4, high=4, low=4, close=4, volume=1, buy=1, sell=0)
        self.add_entry(open=4, high=4, low=3, close=3, volume=1, buy=0, sell=1)

    def test_scenario_down_80_up_50_one_trade(self):
        """
        Chart flow:
        1. Trend goes down 80%
        2. Trend goes up 50%
        """
        self.add_entry(open=10, high=10, low=10, close=10, volume=1, buy=1, sell=0)
        self.add_entry(open=10, high=10, low=2, close=2, volume=1, buy=0, sell=0)
        self.add_entry(open=2, high=3, low=2, close=3, volume=1, buy=0, sell=1)

    def test_scenario_down_10_up_100_down_75_three_trades(self):
        """
        Chart flow:
        1. Trend goes down 10%
        2. Trend goes up 100%
        3. Trend goes down 75%
        """
        self.add_entry(open=10, high=10, low=10, close=10, volume=1, buy=1, sell=0)
        self.add_entry(open=10, high=10, low=9, close=9, volume=1, buy=0, sell=1)
        self.add_entry(open=9, high=9, low=9, close=9, volume=1, buy=1, sell=0)
        self.add_entry(open=9, high=18, low=9, close=18, volume=1, buy=0, sell=1)
        self.add_entry(open=18, high=18, low=18, close=18, volume=1, buy=1, sell=0)
        self.add_entry(open=18, high=18, low=4.5, close=4.5, volume=1, buy=0, sell=1)

    def test_scenario_down_10_up_100_down_75_one_trade(self):
        """
        Chart flow:
        1. Trend goes down 10%
        2. Trend goes up 100%
        3. Trend goes down 75%
        """
        self.add_entry(open=10, high=10, low=10, close=10, volume=1, buy=1, sell=0)
        self.add_entry(open=10, high=10, low=9, close=9, volume=1, buy=0, sell=0)
        self.add_entry(open=9, high=18, low=9, close=18, volume=1, buy=0, sell=0)
        self.add_entry(open=18, high=18, low=4.5, close=4.5, volume=1, buy=0, sell=1)

    def test_scenario_up_100_down_20_down_75_three_trades(self):
        """
        Chart flow:
        1. Trend goes up 100%
        2. Trend goes down 20%
        3. Trend goes down 75%
        """
        self.add_entry(open=5, high=5, low=5, close=5, volume=1, buy=1, sell=0)
        self.add_entry(open=5, high=10, low=5, close=10, volume=1, buy=0, sell=1)
        self.add_entry(open=10, high=10, low=10, close=10, volume=1, buy=1, sell=0)
        self.add_entry(open=10, high=10, low=8, close=8, volume=1, buy=0, sell=1)
        self.add_entry(open=8, high=8, low=8, close=8, volume=1, buy=1, sell=0)
        self.add_entry(open=8, high=8, low=2, close=2, volume=1, buy=0, sell=1)

    def test_scenario_up_100_down_20_down_75_one_trade(self):
        """
        Chart flow:
        1. Trend goes up 100%
        2. Trend goes down 20%
        3. Trend goes down 75%
        """
        self.add_entry(open=5, high=5, low=5, close=5, volume=1, buy=1, sell=0)
        self.add_entry(open=5, high=10, low=5, close=10, volume=1, buy=0, sell=0)
        self.add_entry(open=10, high=10, low=8, close=8, volume=1, buy=0, sell=0)
        self.add_entry(open=8, high=8, low=2, close=2, volume=1, buy=0, sell=1)

    def test_scenario_up_100_down_20_down_75_no_trades(self):
        """
        Chart flow:
        1. Trend goes up 100%
        2. Trend goes down 20%
        3. Trend goes down 75%
        """
        self.add_entry(open=5, high=5, low=5, close=5, volume=1, buy=0, sell=0)
        self.add_entry(open=5, high=10, low=5, close=10, volume=1, buy=0, sell=0)
        self.add_entry(open=10, high=10, low=8, close=8, volume=1, buy=0, sell=0)
        self.add_entry(open=8, high=8, low=2, close=2, volume=1, buy=0, sell=0)

    def multiply_price(self, multiplier: float, trade_action: TradeAction = TradeAction.NOTHING):

        if trade_action == TradeAction.BUY:
            buy, sell = 1, 0
        elif trade_action == TradeAction.SELL:
            buy, sell = 0, 1
        else:
            buy, sell = 0, 0

        last_close_price = self.get(self.current_time, {"close": 1})["close"]
        new_price = last_close_price * multiplier
        return self.add_entry(last_close_price, new_price, last_close_price, new_price, 1, buy, sell)


KeyType = TypeVar("KeyType")


class MockPairFrame(dict):

    def __init__(self, keys: list):
        super().__init__()
        self.frame_keys = keys
        for key in keys:
            self.setdefault(key, MockOHLCVWithSignal(key))

    def __setitem__(self, k: str, v: MockOHLCVWithSignal) -> None:
        if k not in self:
            raise LookupError(f"no pair {k} defined on construction")
        super().__setitem__(k, v)
