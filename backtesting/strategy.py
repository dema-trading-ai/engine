import numpy
import talib as ta

from models.ohlcv import OHLCV
from models.trade import Trade

# ======================================================================
# Strategy-class is responsible for populating indicators / signals
#
# © 2021 DemaTrading.AI
# ======================================================================

class Strategy:
    def populate_indicators(self, past_candles: [OHLCV], current_candle: OHLCV) -> {}:

        return {}

    def populate_buy_signal(self, indicators, current_candle: OHLCV):

        return True

    def populate_sell_signal(self, indicators, current_candle, trade: Trade):
        # print
        if trade.profit_percentage > 2:
            return True
        return False
