# This module contains helper functions that have to do with the config
# file, like validation and currency support

import json
import re
import sys
from datetime import datetime

import numpy as np
from numpy.distutils.command.config import config

from data.datamodule import minute, hour
from .cctx_adapter import create_cctx_exchange
from .validations import validate
from .load_strategy import load_strategy_from_config
from .cli import adjust_config_to_cli


class ConfigModule(object):

    def __init__(self):
        config = read_config()
        validate(config)
        self.config = config
        timeframe = config["timeframe"]
        exchange_str = config["exchange"]
        self.timeframe = parse_timeframe(timeframe)
        self.exchange = create_cctx_exchange(exchange_str, exchange_str)
        backtesting_till_now = config["backtesting-till-now"]
        backtesting_from = config["backtesting-from"]
        backtesting_to = config["backtesting-to"]
        self.backtesting_from, self.backtesting_to = config_from_to(self.exchange, backtesting_from, backtesting_to,
                                                                    backtesting_till_now)

        self.pairs = config["pairs"]
        self.btc_marketchange_ratio = self.load_btc_marketchange()

    def load_btc_marketchange(self):
        print("[INFO] Fetching marketchange of BTC/USDT...")
        begin_data = self.exchange.fetch_ohlcv(symbol='BTC/USDT', timeframe='1m', since=self.backtesting_from, limit=1)
        end_timestamp = int(np.floor(self.backtesting_to / self.timeframe) * self.timeframe)
        end_data = self.exchange.fetch_ohlcv(symbol='BTC/USDT', timeframe='1m', since=end_timestamp, limit=1)

        begin_close_value = begin_data[0][4]
        end_close_value = end_data[0][4]
        return end_close_value / begin_close_value

    def get(self) -> dict:
        pass


def read_config() -> dict:
    print(
        '====================================== \n'
        ' Starting up DEMA BACKTESTING \n'
        '======================================')
    try:
        with open('config.json', 'r') as configfile:
            data = configfile.read()
    except FileNotFoundError:
        raise FileNotFoundError("[ERROR] No config file found.")
    except Exception:
        raise Exception("[ERROR] Something went wrong parsing config file.",
                        sys.exc_info()[0])
    return json.loads(data)


def read_spec() -> list:
    with open("config/specification.json", "r") as f:
        spec = f.read()
    return json.loads(spec)


def print_pairs(config_json):
    coins = ''
    for i in config_json['pairs']:
        coins += str(i) + ' '
    print("[INFO] Watching pairs: %s." % coins)


def parse_timeframe(timeframe_str: str):
    print('[INFO] Configuring timeframe...')

    match = re.match(r"([0-9]+)([mdh])", timeframe_str, re.I)
    if not match:
        raise Exception("[ERROR] Error whilst parsing timeframe")
    items = re.split(r'([0-9]+)', timeframe_str)
    if items[2] == 'm':
        timeframe_time = int(items[1]) * minute
    elif items[2] == 'h':
        timeframe_time = int(items[1]) * hour
    else:
        raise Exception("[ERROR] Error whilst parsing timeframe")  # TODO
    return timeframe_time


def config_from_to(exchange, backtesting_from: int, backtesting_to: int, backtesting_till_now: bool) -> tuple[int, int]:
    test_from = backtesting_from
    test_to = backtesting_to
    test_till_now = backtesting_till_now
    today_ms = exchange.milliseconds()

    backtesting_from = exchange.parse8601("%sT00:00:00Z" % test_from)
    backtesting_to = exchange.parse8601("%sT00:00:00Z" % test_to)

    if test_till_now or today_ms < backtesting_to:
        test_to = datetime.fromtimestamp(today_ms / 1000.0).strftime("%Y-%m-%d")
        print('[INFO] Changed %s to %s.' % (backtesting_to, test_to))
        backtesting_to = today_ms

    if backtesting_from >= backtesting_to:
        raise Exception("[ERROR] Backtesting periods are configured incorrectly.")
    print('[INFO] Gathering data from %s until %s.' % (test_from, test_to))
    return backtesting_to, backtesting_from
