import ccxt
import re
from models.ohlcv import OHLCV

# ======================================================================
# DataModule is responsible for downloading OHLCV data, preparing it
# and activating backtesting methods
#
# © 2021 DemaTrading.AI - Tijs Verbeek
# ======================================================================

msec = 1000
minute = 60 * msec
hour = 60 * minute
day = 24 * hour


class DataModule:
    config = None
    exchange = None
    timeframe_calc = None

    backtesting_from = None
    backtesting_to = None

    backtesting_module = None
    history_data = {}

    def __init__(self, config, backtesting_module):
        print('[INFO] Starting DEMA Data-module...')
        self.config = config
        self.backtesting_module = backtesting_module
        self.config_timeframe_calc()
        self.load_exchange()

    def load_exchange(self):
        print('[INFO] Connecting to exchange...')
        exchange_id = self.config['exchange']

        # Try to get exchange based on config param 'exchange'
        try:
            self.exchange = getattr(ccxt, exchange_id)
            self.exchange = self.exchange()
            print("[INFO] Connected to exchange: %s." % self.config['exchange'])
        except AttributeError:
            print("[ERROR] Exchange %s could not be found!" % exchange_id)
            raise SystemExit

        # Check whether exchange supports OHLC
        if not self.exchange.has["fetchOHLCV"]:
            print("[ERROR] Cannot load data from %s" % self.config['exchange'])
            raise SystemExit

        # Check whether exchange supports requested timeframe
        if (not hasattr(self.exchange, 'timeframes')) or (self.config['timeframe'] not in self.exchange.timeframes):
            print("[ERROR] Requested timeframe is not available from %s" % self.config['exchange'])
            raise SystemExit

        self.load_markets()

    def load_markets(self):
        self.exchange.load_markets()
        self.config_from_to()
        self.load_historical_data()

    def load_historical_data(self):
        for pair in self.config['pairs']:
            self.history_data[pair] = []
            self.download_data_for_pair(pair)
        self.backtesting_module.start_backtesting(self.history_data, self.backtesting_from, self.backtesting_to)

    def parse_ohcl_data(self, data, pair):
        return_value = []
        for candle in data:
            temp = OHLCV(candle[0], candle[1], candle[2], candle[3], candle[4], candle[5], pair)
            return_value.append(temp)
        return return_value

    def download_data_for_pair(self, pair):
        testing_from = self.backtesting_from
        testing_to = self.backtesting_to
        timeframe = self.config['timeframe']
        print("[INFO] Downloading %s's data" % pair)

        while testing_from < testing_to:
            result = self.exchange.fetch_ohlcv(pair, timeframe, testing_from)
            self.history_data[pair] += self.parse_ohcl_data(result, pair)
            testing_from += len(result) * self.timeframe_calc

        print("[INFO] [%s] %s candles downloaded" % (pair, len(self.history_data[pair])))

    def config_timeframe_calc(self):
        print('[INFO] Configuring timeframe')
        timeframe = self.config['timeframe']
        match = re.match(r"([0-9]+)([mdh])", timeframe, re.I)
        if not match:
            print("[ERROR] Error whilst parsing timeframe")
            raise SystemExit
        if match:
            items = re.split(r'([0-9]+)', timeframe)
            if items[2] == 'm':
                self.timeframe_calc = int(items[1]) * minute
            if items[2] == 'h':
                self.timeframe_calc = int(items[1]) * hour

    def config_from_to(self):
        test_from = self.config['backtesting-from']
        test_to = self.config['backtesting-to']
        test_till_now = self.config['backtesting-till-now']

        if test_till_now == 'True':
            print('[INFO] Downloading data from %s until now' % test_from)
            self.backtesting_to = self.exchange.milliseconds()
            self.backtesting_from = self.exchange.parse8601("%sT00:00:00Z" % test_from)
        elif test_till_now == 'False':
            print('[INFO] Downloading data from %s until %s' % (test_from, test_to))
            self.backtesting_from =self.exchange.parse8601("%sT00:00:00Z" % test_from)
            self.backtesting_to = self.exchange.parse8601("%sT00:00:00Z" % test_to)
        else:
            print("[ERROR] Something went wrong parsing config. Please use yyyy-mm-dd format at 'backtesting-from', 'backtesting-to'")