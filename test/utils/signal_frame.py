class MockOHLCVWithSignal(dict):

    def add_entry(self, time: int, open=1, high=1, low=1, close=1, volume=1, buy=0, sell=0):
        self.update({time: {'time': time,
                            'open': open,
                            'high': high,
                            'low': low,
                            'close': close,
                            'volume': volume,
                            'pair': 'BTC/USDT',
                            'buy': buy,
                            'sell': sell}})
        return self


class MockPairFrame(dict[str, MockOHLCVWithSignal]):
    def __getitem__(self, k: str) -> MockOHLCVWithSignal:
        return self.setdefault(k, MockOHLCVWithSignal())