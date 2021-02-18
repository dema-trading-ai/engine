from collections import namedtuple

import ccxt
import re
import json
import sys
from models.ohlcv import OHLCV
from models.ohlcv_encoder import OHLCVEncoder
from os import path
import os

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
    exchange = None
    timeframe_calc = None

    backtesting_from = None
    backtesting_to = None

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
            if not self.check_for_datafile_existence(pair, self.config['timeframe']):
                #datafile doesn't exist. Start downloading data, create datafile
                print("[INFO] Did not find datafile for %s" % pair)
                self.history_data[pair] = []
                self.download_data_for_pair(pair, True)
                continue
            elif self.does_datafile_cover_backtesting_period(pair, self.config['timeframe']):
                #load data from datafile instead of exchange
                self.history_data[pair] = []
                self.read_data_from_datafile(pair, self.config['timeframe'])
            elif not self.does_datafile_cover_backtesting_period(pair, self.config['timeframe']):
                #remove file, download data from exchange, create new datafile
                self.history_data[pair] = []
                self.delete_file(pair, self.config['timeframe'])
                self.download_data_for_pair(pair, True)

        self.backtesting_module.start_backtesting(self.history_data, self.backtesting_from, self.backtesting_to)

    def parse_ohcl_data(self, data, pair):
        return_value = []
        for candle in data:
            temp = OHLCV(candle[0], candle[1], candle[2], candle[3], candle[4], candle[5], pair)
            return_value.append(temp)
        return return_value

    def download_data_for_pair(self, pair, write_to_datafile):
        testing_from = self.backtesting_from
        testing_to = self.backtesting_to
        timeframe = self.config['timeframe']
        print("[INFO] Downloading %s's data" % pair)

        while testing_from < testing_to:
            result = self.exchange.fetch_ohlcv(pair, timeframe, testing_from)
            self.history_data[pair] += self.parse_ohcl_data(result, pair)
            testing_from += len(result) * self.timeframe_calc

        if write_to_datafile:
            self.create_new_datafile(self.history_data[pair], pair, timeframe)

        print("[INFO] [%s] %s candles downloaded" % (pair, len(self.history_data[pair])))

    def download_data_for_pair_in_timespan(self, from_time, to_time):
        return

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
            print('[INFO] Gathering data from %s until now' % test_from)
            self.backtesting_to = self.exchange.milliseconds()
            self.backtesting_from = self.exchange.parse8601("%sT00:00:00Z" % test_from)
        elif test_till_now == 'False':
            print('[INFO] Gathering data from %s until %s' % (test_from, test_to))
            self.backtesting_from = self.exchange.parse8601("%sT00:00:00Z" % test_from)
            self.backtesting_to = self.exchange.parse8601("%sT00:00:00Z" % test_to)
        else:
            print("[ERROR] Something went wrong parsing config. Please use yyyy-mm-dd format at 'backtesting-from', 'backtesting-to'")

    def check_for_datafile_existence(self, pair, timeframe) -> bool:
        filename = self.generate_datafile_name(pair, timeframe)
        dirpath = "data/backtesting-data/" + self.config["exchange"] + "/" + filename

        if not path.exists("data/backtesting-data/%s" % self.config["exchange"]):
            try:
                os.makedirs("data/backtesting-data/%s" % self.config["exchange"])
            except OSError:
                print("Creation of the directory %s failed" % path)
            else:
                print("Successfully created the directory %s " % path)
                return False
        return path.exists(dirpath)

    def read_data_from_datafile(self, pair, timeframe):
        filename = self.generate_datafile_name(pair, timeframe)
        filepath = "data/backtesting-data/" + self.config["exchange"] + "/" + filename
        try:
            with open(filepath, 'r') as datafile:
                data = datafile.read()
        except FileNotFoundError:
            print("[ERROR] Backtesting datafile was not found.")
            raise SystemExit
        except:
            print("[ERROR] Something went wrong loading datafile", sys.exc_info()[0])
            raise SystemExit

        historic_data = json.loads(data)
        print("[INFO] Loading historic data of %s from existing datafile." % pair)
        for tick in historic_data['ohlcv']:
            parsed_tick = json.loads(tick, object_hook=self.customOHLCVDecoder)
            self.history_data[pair].append(parsed_tick)

    def create_new_datafile(self, data: [OHLCV], pair, timeframe):
        data_for_file = {}
        filename = self.generate_datafile_name(pair, timeframe)
        filepath = "data/backtesting-data/" + self.config["exchange"] + "/" + filename
        data_for_file["from"] = self.backtesting_from
        data_for_file["to"] = self.backtesting_to
        data_for_file["ohlcv"] = []
        for tick in data:
            json_ohlcv = OHLCVEncoder().encode(tick)
            data_for_file["ohlcv"].append(json_ohlcv)
        with open(filepath, 'w') as outfile:
            json.dump(data_for_file, outfile)

    def generate_datafile_name(self, pair, timeframe):
        formatted_pair = pair.split('/')
        return "data-"+formatted_pair[0]+formatted_pair[1]+timeframe+".json"

    def delete_file(self, pair, timeframe):
        filename = self.generate_datafile_name(pair, timeframe)
        filepath = "data/backtesting-data/" + self.config["exchange"] + "/" + filename
        os.remove(filepath)

    def does_datafile_cover_backtesting_period(self, pair, timeframe) -> bool:
        filename = self.generate_datafile_name(pair, timeframe)
        filepath = "data/backtesting-data/%s/%s" % (self.config['exchange'], filename)
        try:
            with open(filepath, 'r') as datafile:
                data = datafile.read()
        except FileNotFoundError:
            print("[ERROR] Backtesting datafile was not found.")
            return False
        except:
            print("[ERROR] Something went wrong loading datafile", sys.exc_info()[0])
            return False

        historic_data = json.loads(data)
        if historic_data["from"] == self.backtesting_from and historic_data["to"] == self.backtesting_to:
            return True
        return False

    def customOHLCVDecoder(self, ohlcv_dict):
        return namedtuple('OHLCV', ohlcv_dict.keys())(*ohlcv_dict.values())


