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
# © 2021 DemaTrading.AI
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

    def load_exchange(self) -> None:
        """
        Method checks for requested exchange existence
        checks for exchange OHLCV compatibility
        checks for timeframe support
        loads markets if no errors occur

        :return: None
        :rtype: None
        """
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
            print("[ERROR] Cannot load data from %s because it doesn't support OHLCV-data" % self.config['exchange'])
            raise SystemExit

        # Check whether exchange supports requested timeframe
        if (not hasattr(self.exchange, 'timeframes')) or (self.config['timeframe'] not in self.exchange.timeframes):
            print("[ERROR] Requested timeframe is not available from %s" % self.config['exchange'])
            raise SystemExit

        self.load_markets()

    def load_markets(self) -> None:
        self.exchange.load_markets()
        self.config_from_to()
        self.load_historical_data()

    def load_historical_data(self) -> None:
        """
        Method checks for datafile existence, if not existing, download data and save to file

        :return: None
        :rtype: None
        """
        for pair in self.config['pairs']:
            if not self.check_for_datafile_existence(pair, self.config['timeframe']):
                # datafile doesn't exist. Start downloading data, create datafile
                print("[INFO] Did not find datafile for %s" % pair)
                self.history_data[pair] = []
                self.download_data_for_pair(pair, True)
            elif self.does_datafile_cover_backtesting_period(pair, self.config['timeframe']):
                # load data from datafile instead of exchange
                self.history_data[pair] = []
                self.read_data_from_datafile(pair, self.config['timeframe'])
            elif not self.does_datafile_cover_backtesting_period(pair, self.config['timeframe']):
                # remove file, download data from exchange, create new datafile
                self.history_data[pair] = []
                self.delete_file(pair, self.config['timeframe'])
                self.download_data_for_pair(pair, True)

        self.backtesting_module.start_backtesting(self.history_data, self.backtesting_from, self.backtesting_to)

    def parse_ohcl_data(self, data, pair: str) -> [OHLCV]:
        """
        :param data: OHLCV data provided by CCXT in array format []
        :type data: float array
        :param pair: Certain coin pair in "AAA/BBB" format
        :type pair: string
        :return: OHLCV array
        :rtype: [OHLCV]
        """
        return_value = []
        for candle in data:
            temp = OHLCV(candle[0], candle[1], candle[2], candle[3], candle[4], candle[5], pair)
            return_value.append(temp)
        return return_value

    def download_data_for_pair(self, pair: str, write_to_datafile: bool) -> None:
        """
        :param pair: Certain coin pair in "AAA/BBB" format
        :type pair: string
        :param write_to_datafile: Whether to write downloaded data to jsonfile
        :type write_to_datafile: boolean
        :return: None
        :rtype: None
        """
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

    def config_timeframe_calc(self) -> None:
        """
        Method checks for valid timeframe input in config file.
        Besides sets self.timeframe_calc property, which is used
        to calculate how much time has passed based on an amount of candles
        so:

        self.timeframe_calc * 10 candles passed = milliseconds passed
        """
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

    def config_from_to(self) -> None:
        """
        This method sets the self.backtesting_to / backtesting_from properties
        with 8601 parsed timestamp

        :return: None
        :rtype: None
        """
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
            print(
                "[ERROR] Something went wrong parsing config. Please use yyyy-mm-dd format at 'backtesting-from', 'backtesting-to'")

    def check_for_datafile_existence(self, pair, timeframe) -> bool:
        """
        :param pair: Certain coin pair in "AAA/BBB" format
        :type pair: string
        :param timeframe: Time frame of coin pair f.e. "1h" / "5m"
        :type timeframe: string
        :return: Returns whether datafile for specified pair / timeframe already exists
        :rtype: boolean
        """
        coin, base = pair.split('/')
        dirpath = os.path.join("data/backtesting-data", self.config["exchange"], coin, base)
        exhange_path = os.path.join("data/backtesting-data", self.config["exchange"])
        self.create_directory_if_not_exists(exhange_path)
        return path.exists(dirpath)

    def create_directory_if_not_exists(self, directory: str) -> None:
        """
        :param directory: string of path to directory
        :type directory: string
        :return: None
        :rtype: None
        """
        if not path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError:
                print("Creation of the directory %s failed" % path)
            else:
                print("Successfully created the directory %s " % path)

    def read_data_from_datafile(self, pair, timeframe) -> None:
        """
        When datafile is covering requested backtesting period,
        this method reads the data from the files. Saves this in
        self.historical_data

        :param pair: Certain coin pair in "AAA/BBB" format
        :type pair: string
        :param timeframe: Time frame of coin pair f.e. "1h" / "5m"
        :type timeframe: string
        :return: None
        :rtype: None
        """
        filename = self.generate_datafile_name(pair, timeframe)
        filepath = os.path.join("data/backtesting-data/", self.config["exchange"], filename)
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

    def create_new_datafile(self, data: [OHLCV], pair: str, timeframe: str) -> None:
        """
        Method creates new json datafile for pair in timeframe

        :param data: Downloaded data to write to the datafile
        :type data: OHLCV array
        :param pair: Certain coin pair in "AAA/BBB" format
        :type pair: string
        :param timeframe: Time frame of coin pair f.e. "1h" / "5m"
        :type timeframe: string
        :return: None
        :rtype: None
        """
        data_for_file = {}
        filename = self.generate_datafile_name(pair, timeframe)
        filepath = os.path.join("data/backtesting-data/", self.config["exchange"], filename)
        data_for_file["from"] = self.backtesting_from
        data_for_file["to"] = self.backtesting_to
        data_for_file["ohlcv"] = []
        for tick in data:
            json_ohlcv = OHLCVEncoder().encode(tick)
            data_for_file["ohlcv"].append(json_ohlcv)
        with open(filepath, 'w') as outfile:
            json.dump(data_for_file, outfile)

    def generate_datafile_name(self, pair: str, timeframe: str) -> str:
        """
        :param pair: Certain coin pair in "AAA/BBB" format
        :type pair: string
        :param timeframe: Time frame of coin pair f.e. "1h" / "5m"
        :type timeframe: string
        :return: returns a filename for specified pair / timeframe
        :rtype: string
        """
        formatted_pair = pair.split('/')
        return "data-" + formatted_pair[0] + formatted_pair[1] + timeframe + ".json"

    def delete_file(self, pair: str, timeframe: str):
        """
        Method removes existing datafile, as it does not cover requested
        backtesting period.

        :param pair: Certain coin pair in "AAA/BBB" format
        :type pair: string
        :param timeframe: Time frame of coin pair f.e. "1h" / "5m"
        :type timeframe: string
        :return: None
        :rtype: None
        """
        filename = self.generate_datafile_name(pair, timeframe)
        filepath = os.path.join("data/backtesting-data/", self.config["exchange"], filename)
        os.remove(filepath)

    def does_datafile_cover_backtesting_period(self, pair: str, timeframe: str) -> bool:
        """
        :param pair: Certain coin pair in "AAA/BBB" format
        :type pair: string
        :param timeframe: Time frame of coin pair f.e. "1h" / "5m"
        :type timeframe: string
        :return: Returns True if datafile covers set backtesting timespan, False if not
        :rtype: boolean
        """
        filename = self.generate_datafile_name(pair, timeframe)
        filepath = os.path.join("data/backtesting-data/", self.config["exchange"], filename)
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

    def customOHLCVDecoder(self, ohlcv_dict) -> namedtuple:
        """
        This method is used for reading ohlcv-data from saved json datafiles.

        :param ohlcv_dict: dictionary-format ohlcv-model, which is 1 candle in specified timeframe
        :type ohlcv_dict: json-format ohlcv-model
        :return: named tuple with OHLCV properties (more or less the same as the model)
        :rtype: namedtuple
        """
        return namedtuple('OHLCV', ohlcv_dict.keys())(*ohlcv_dict.values())
