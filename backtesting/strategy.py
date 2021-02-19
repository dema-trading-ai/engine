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
        """
        :param past_candles: Array of candle-data (OHLCV models)
        :type past_candles: [OHLCV]
        :param current_candle: Last candle
        :type current_candle: OHLCV model
        :return: dictionary filled with indicator-data
        :rtype: dictionary
        """

        return {}

    def populate_buy_signal(self, indicators, current_candle: OHLCV) -> bool:
        """
        :param indicators: indicator dictionary created by populate_indicators method
        :type indicators: dictionary
        :param current_candle: last candle
        :type current_candle: OHLCV model
        :return: returns whether to buy or not buy specified coin (True = buy, False = skip)
        :rtype: boolean
        """

        return True

    def populate_sell_signal(self, indicators, current_candle, trade: Trade) -> bool:
        """
        :param indicators: indicator dictionary created by populate_indicators method
        :type indicators: dictionary
        :param current_candle: last candle
        :type current_candle: OHLCV model
        :param trade: current open trade
        :type trade: Trade model
        :return: returns whether to close or not close specified trade (True = sell, False = skip)
        :rtype: boolean
        """
        # print
        if trade.profit_percentage > 2:
            return True
        return False
