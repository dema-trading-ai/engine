# ======================================================================
# OHLCV Class is used for candle-data served by CCXT
#
# © 2021 DemaTrading.AI - Tijs Verbeek
# ======================================================================

class OHLCV:
    time = None
    open = None
    high = None
    low = None
    close = None
    volume = None
    pair = None

    def __init__(self, time, open, high, low, close, volume, pair):
        self.time = time
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.pair = pair
