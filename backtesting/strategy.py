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
    min_candles = 21

    def generate_indicators(self, past_candles: [OHLCV], current_candle: OHLCV) -> {}:
        """
        :param past_candles: Array of candle-data (OHLCV models)
        :type past_candles: [OHLCV]
        :param current_candle: Last candle
        :type current_candle: OHLCV model
        :return: dictionary filled with indicator-data
        :rtype: dictionary
        """
        indicators = {}
        if (len(past_candles)+1) < self.min_candles:
            return indicators

        # dinges = numpy.stack(past_candles).astype(OHLCV)
        #
        # close = []
        # volume = []
        # for candle in past_candles:
        #     close.append(candle.close)
        #     volume.append(candle.volume)
        # close.append(current_candle)
        #
        # indicators['SMA21'] = ta.MA(numpy.array(close), timeperiod=21)
        # indicators['RSI'] = ta.RSI(numpy.array(close))
        return indicators

    def buy_signal(self, indicators, current_candle: OHLCV) -> bool:
        """
        :param indicators: indicator dictionary created by generate_indicators method
        :type indicators: dictionary
        :param current_candle: last candle
        :type current_candle: OHLCV model
        :return: returns whether to buy or not buy specified coin (True = buy, False = skip)
        :rtype: boolean
        """

        return True

    def sell_signal(self, indicators, current_candle, trade: Trade) -> bool:
        """
        :param indicators: indicator dictionary created by generate_indicators method
        :type indicators: dictionary
        :param current_candle: last candle
        :type current_candle: OHLCV model
        :param trade: current open trade
        :type trade: Trade model
        :return: returns whether to close or not close specified trade (True = sell, False = skip)
        :rtype: boolean
        """
        # # print
        # if trade.profit_percentage > 2:
        #     return True
        return False
