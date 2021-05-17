from typing import TypeVar


class MockOHLCVWithSignal(dict, object):
    __key: object
    __current_time: int

    def __init__(self, key):
        super().__init__()
        self.__key = key
        self.__current_time = 0

    def add_entry(self, open=1, high=1, low=1, close=1, volume=1, buy=0, sell=0, stoploss=0):
        self.__current_time += 1
        self.update({self.__current_time: {'time': self.__current_time,
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


