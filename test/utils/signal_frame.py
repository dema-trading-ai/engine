import sys
from enum import Enum
from typing import TypeVar
from utils.error_handling import ErrorOutput

# Define different timestep values
WEEKLY = 604800000  # 7 days in milliseconds
DAILY = 86400000  # 24 hours in milliseconds
TWELVE_HOURS = 43200000  # 12 hours in milliseconds
EIGHT_HOURS = 28800000  # 8 hours in milliseconds
SIX_HOURS = 21600000  # 6 hours in milliseconds
THIRTY_MIN = 1800000  # 30 minutes in milliseconds
ONE_MIL = 1  # 1 millisecond


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
        self.current_time = 1577833200000  # 2020-01-01

    def set_starting_time(self, starting_time):
        self.current_time = starting_time

    def add_entry(self, open=1., high=1., low=1., close=1., volume=1., buy=0, sell=0, stoploss=0, timestep=DAILY):
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
        self.current_time += timestep
        return self

    def test_scenario_flat_no_trades(self, timestep=THIRTY_MIN):
        """
        Chart flow:
        1. Trend stays the same
        """
        self.add_entry(open=2, high=2, low=2, close=2, buy=0, sell=0, timestep=timestep)
        self.add_entry(open=2, high=2, low=2, close=2, buy=0, sell=0, timestep=timestep)

    def test_scenario_up_no_trades(self, timestep=THIRTY_MIN):
        """
        Chart flow:
        1. Trend stays the same
        """
        self.add_entry(open=2, high=2, low=2, close=2, buy=0, sell=0, timestep=timestep)
        self.add_entry(open=2, high=4, low=2, close=4, buy=0, sell=0, timestep=timestep)

    def test_scenario_flat_one_trade(self, timestep=THIRTY_MIN):
        """
        Chart flow:
        1. Trend stays the same
        """
        self.add_entry(open=2, high=2, low=2, close=2, buy=1, sell=0, timestep=timestep)
        self.add_entry(open=2, high=2, low=2, close=2, buy=0, sell=1, timestep=timestep)

    def test_scenario_flat_one_trade_no_sell(self, timestep=THIRTY_MIN):
        """
        Chart flow:
        1. Trend stays the same (but no sell signal)
        """
        self.add_entry(open=2, high=2, low=2, close=2, buy=1, sell=0, timestep=timestep)
        self.add_entry(open=2, high=2, low=2, close=2, buy=0, sell=0, timestep=timestep)

    def test_scenario_down_50_one_trade(self, timestep=THIRTY_MIN):
        """
        Chart flow:
        1. Trend goes down 50%
        """
        self.add_entry(open=2, high=2, low=2, close=2, buy=1, sell=0, timestep=timestep)
        self.add_entry(open=2, high=2, low=1, close=1, buy=0, sell=1, timestep=timestep)

    def test_scenario_down_50_one_trade_no_sell(self, timestep=THIRTY_MIN):
        """
        Chart flow:
        1. Trend goes down 50%
        """
        self.add_entry(open=2, high=2, low=2, close=2, buy=1, sell=0, timestep=timestep)
        self.add_entry(open=2, high=2, low=1, close=1, buy=0, sell=0, timestep=timestep)

    def test_scenario_down_75_one_trade(self, timestep=THIRTY_MIN):
        """
        Chart flow:
        1. Trend goes down 75%
        """
        self.add_entry(open=4, high=4, low=4, close=4, buy=1, sell=0, timestep=timestep)
        self.add_entry(open=4, high=4, low=1, close=1, buy=0, sell=1, timestep=timestep)

    def test_scenario_up_50_one_trade(self, timestep=THIRTY_MIN):
        """
        Chart flow:
        1. Trend goes up 50%
        """
        self.add_entry(open=2, high=2, low=2, close=2, buy=1, sell=0, timestep=timestep)
        self.add_entry(open=2, high=3, low=2, close=3, buy=0, sell=1, timestep=timestep)

    def test_scenario_up_100_one_trade(self, timestep=THIRTY_MIN):
        """
        Chart flow:
        1. Trend goes up 100%
        """
        self.add_entry(open=1, high=1, low=1, close=1, buy=1, sell=0, timestep=timestep)
        self.add_entry(open=1, high=2, low=1, close=2, buy=0, sell=1, timestep=timestep)

    def test_scenario_up_100_one_trade_no_sell(self, timestep=THIRTY_MIN):
        """
        Chart flow:
        1. Trend goes up 100%
        """
        self.add_entry(open=1, high=1, low=1, close=1, buy=1, sell=0, timestep=timestep)
        self.add_entry(open=1, high=2, low=1, close=2, buy=0, sell=0, timestep=timestep)

    def test_scenario_up_100_down_50_one_trade(self, timestep=THIRTY_MIN):
        """
        Chart flow:
        1. Trend goes up 100%
        2. Trend goes down 50%
        """
        self.add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0, timestep=timestep)
        self.add_entry(open=2, high=4, low=2, close=4, volume=1, buy=0, sell=0, timestep=timestep)
        self.add_entry(open=4, high=4, low=2, close=2, volume=1, buy=0, sell=1, timestep=timestep)

    def test_scenario_up_100_down_75_one_trade(self, timestep=THIRTY_MIN):
        """
        Chart flow:
        1. Trend goes up 100%
        2. Trend goes down 75%
        """
        self.add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0, timestep=timestep)
        self.add_entry(open=2, high=4, low=2, close=4, volume=1, buy=0, sell=0, timestep=timestep)
        self.add_entry(open=4, high=4, low=3, close=3, volume=1, buy=0, sell=1, timestep=timestep)

    def test_scenario_up_100_down_75_two_trades(self, timestep=THIRTY_MIN):
        """
        Chart flow:
        1. Trend goes up 100%
        2. Trend goes down 75%
        """
        self.add_entry(open=2, high=2, low=2, close=2, volume=1, buy=1, sell=0, timestep=timestep)
        self.add_entry(open=2, high=4, low=2, close=4, volume=1, buy=0, sell=1, timestep=timestep)
        self.add_entry(open=4, high=4, low=4, close=4, volume=1, buy=1, sell=0, timestep=timestep)
        self.add_entry(open=4, high=4, low=3, close=3, volume=1, buy=0, sell=1, timestep=timestep)

    def test_scenario_down_80_up_50_one_trade(self, timestep=THIRTY_MIN):
        """
        Chart flow:
        1. Trend goes down 80%
        2. Trend goes up 50%
        """
        self.add_entry(open=10, high=10, low=10, close=10, volume=1, buy=1, sell=0, timestep=timestep)
        self.add_entry(open=10, high=10, low=2, close=2, volume=1, buy=0, sell=0, timestep=timestep)
        self.add_entry(open=2, high=3, low=2, close=3, volume=1, buy=0, sell=1, timestep=timestep)

    def test_scenario_down_10_up_100_down_75_three_trades(self, timestep=THIRTY_MIN):
        """
        Chart flow:
        1. Trend goes down 10%
        2. Trend goes up 100%
        3. Trend goes down 75%
        """
        self.add_entry(open=10, high=10, low=10, close=10, volume=1, buy=1, sell=0, timestep=timestep)
        self.add_entry(open=10, high=10, low=9, close=9, volume=1, buy=0, sell=1, timestep=timestep)
        self.add_entry(open=9, high=9, low=9, close=9, volume=1, buy=1, sell=0, timestep=timestep)
        self.add_entry(open=9, high=18, low=9, close=18, volume=1, buy=0, sell=1, timestep=timestep)
        self.add_entry(open=18, high=18, low=18, close=18, volume=1, buy=1, sell=0, timestep=timestep)
        self.add_entry(open=18, high=18, low=4.5, close=4.5, volume=1, buy=0, sell=1, timestep=timestep)

    def test_scenario_down_10_up_100_down_75_one_trade(self, timestep=THIRTY_MIN):
        """
        Chart flow:
        1. Trend goes down 10%
        2. Trend goes up 100%
        3. Trend goes down 75%
        """
        self.add_entry(open=10, high=10, low=10, close=10, volume=1, buy=1, sell=0, timestep=timestep)
        self.add_entry(open=10, high=10, low=9, close=9, volume=1, buy=0, sell=0, timestep=timestep)
        self.add_entry(open=9, high=18, low=9, close=18, volume=1, buy=0, sell=0, timestep=timestep)
        self.add_entry(open=18, high=18, low=4.5, close=4.5, volume=1, buy=0, sell=1, timestep=timestep)

    def test_scenario_up_100_down_20_down_75_three_trades(self, timestep=THIRTY_MIN):
        """
        Chart flow:
        1. Trend goes up 100%
        2. Trend goes down 20%
        3. Trend goes down 75%
        """
        self.add_entry(open=5, high=5, low=5, close=5, volume=1, buy=1, sell=0, timestep=timestep)
        self.add_entry(open=5, high=10, low=5, close=10, volume=1, buy=0, sell=1, timestep=timestep)
        self.add_entry(open=10, high=10, low=10, close=10, volume=1, buy=1, sell=0, timestep=timestep)
        self.add_entry(open=10, high=10, low=8, close=8, volume=1, buy=0, sell=1, timestep=timestep)
        self.add_entry(open=8, high=8, low=8, close=8, volume=1, buy=1, sell=0, timestep=timestep)
        self.add_entry(open=8, high=8, low=2, close=2, volume=1, buy=0, sell=1, timestep=timestep)

    def test_scenario_up_100_down_20_down_75_one_trade(self, timestep=THIRTY_MIN):
        """
        Chart flow:
        1. Trend goes up 100%
        2. Trend goes down 20%
        3. Trend goes down 75%
        """
        self.add_entry(open=5, high=5, low=5, close=5, volume=1, buy=1, sell=0, timestep=timestep)
        self.add_entry(open=5, high=10, low=5, close=10, volume=1, buy=0, sell=0, timestep=timestep)
        self.add_entry(open=10, high=10, low=8, close=8, volume=1, buy=0, sell=0, timestep=timestep)
        self.add_entry(open=8, high=8, low=2, close=2, volume=1, buy=0, sell=1, timestep=timestep)

    def test_scenario_up_100_down_20_down_75_one_trade_long_timesteps(self, timestep=THIRTY_MIN):
        """
        Chart flow:
        1. Trend goes up 100%
        2. Trend goes down 20%
        3. Trend goes down 75%
        """
        self.add_entry(open=5, high=5, low=5, close=5, volume=1, buy=1, sell=0, timestep=timestep)
        self.add_entry(open=5, high=10, low=5, close=10, volume=1, buy=0, sell=0, timestep=timestep)
        self.add_entry(open=10, high=10, low=10, close=10, volume=1, buy=0, sell=0, timestep=timestep)
        self.add_entry(open=10, high=10, low=8, close=8, volume=1, buy=0, sell=0, timestep=timestep)
        self.add_entry(open=8, high=8, low=8, close=8, volume=1, buy=0, sell=0, timestep=timestep)
        self.add_entry(open=8, high=8, low=2, close=2, volume=1, buy=0, sell=1, timestep=timestep)

    def test_scenario_up_100_down_20_down_75_no_trades(self, timestep=THIRTY_MIN):
        """
        Chart flow:
        1. Trend goes up 100%
        2. Trend goes down 20%
        3. Trend goes down 75%
        """
        self.add_entry(open=5, high=5, low=5, close=5, volume=1, buy=0, sell=0, timestep=timestep)
        self.add_entry(open=5, high=10, low=5, close=10, volume=1, buy=0, sell=0, timestep=timestep)
        self.add_entry(open=10, high=10, low=8, close=8, volume=1, buy=0, sell=0, timestep=timestep)
        self.add_entry(open=8, high=8, low=2, close=2, volume=1, buy=0, sell=0, timestep=timestep)

    def test_scenario_up_100_one_trade_down_20(self, timestep=THIRTY_MIN):
        """
        Chart flow:
        1. Trend goes up 100%
        2. Trend goes down 20%
        """
        self.add_entry(open=5, high=5, low=5, close=5, volume=1, buy=1, sell=0, timestep=timestep)
        self.add_entry(open=5, high=10, low=5, close=10, volume=1, buy=0, sell=1, timestep=timestep)
        self.add_entry(open=10, high=10, low=8, close=8, volume=1, buy=0, sell=0, timestep=timestep)

    def test_scenario_down_40_one_trade_up_80(self, timestep=THIRTY_MIN):
        """
        Chart flow:
        1. Trend goes down 40%
        2. Trend goes up 80%
        """
        self.add_entry(open=5, high=5, low=5, close=5, volume=1, buy=1, sell=0, timestep=timestep)
        self.add_entry(open=5, high=5, low=3, close=3, volume=1, buy=0, sell=1, timestep=timestep)
        self.add_entry(open=3, high=5.4, low=3, close=5.4, volume=1, buy=0, sell=0, timestep=timestep)

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

    def generate_trades(self, days: int, timestep=DAILY) -> None:
        """
        Generates a high number of trades for tests where a few trades cannot represent what is being tested
        """

        for _ in range(days):
            self.test_scenario_up_100_down_75_one_trade(timestep=timestep)


KeyType = TypeVar("KeyType")


class MockPairFrame(dict):

    def __init__(self, keys: list):
        super().__init__()
        self.frame_keys = keys
        for key in keys:
            self.setdefault(key, MockOHLCVWithSignal(key))

    def __setitem__(self, k: str, v: MockOHLCVWithSignal) -> None:
        try:
            if k not in self:
                raise LookupError()
        except LookupError:
            ErrorOutput(sys.exc_info(),
                        add_info=f"No pair {k} defined on construction",
                        stop=True).print_error()
        super().__setitem__(k, v)
