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

    def test_scenario_1(self):
        """
        Chart flow:
        1. Trend stays the same
        """
        self.add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0)
        self.add_entry(open=2, high=2, low=2, close=2, volume=1, buy=0, sell=1)

    def test_scenario_2(self):
        """
        Chart flow:
        1. Trend stays the same (but no sell signal)
        """
        self.add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0)
        self.add_entry(open=2, high=2, low=2, close=2, volume=1, buy=0, sell=0)

    def test_scenario_3(self):
        """
        Chart flow:
        1. Trend goes down 50%
        """
        self.add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0)
        self.add_entry(open=2, high=2, low=1, close=1, volume=1, buy=0, sell=1)

    def test_scenario_4(self):
        """
        Chart flow:
        1. Trend goes up 50%
        """
        self.add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0)
        self.add_entry(open=2, high=3, low=2, close=3, volume=1, buy=0, sell=1)

    def test_scenario_5(self):
        """
        Chart flow:
        1. Trend goes down  
        2. Trend goes up
        """
        self.add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0)
        self.add_entry(open=2, high=3, low=2, close=3, volume=1, buy=0, sell=1)

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
