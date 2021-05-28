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
