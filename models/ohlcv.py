# ======================================================================
# OHLCV Class is used for candle-data served by CCXT
#
# © 2021 DemaTrading.AI
# ======================================================================


class OHLCV:

    
    def __init__(self, time, open, high, low, close, volume, pair):
        self.time = time
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.pair = pair
