# This module contains helper functions that have to do with the config
# file, like validation and currency support

import json
import re
import sys
from contextlib import asynccontextmanager
from datetime import datetime

import numpy as np

from utils.utils import get_plot_indicators
from .strategy_definition import StrategyDefinition
from .cctx_adapter import create_cctx_exchange
from .currencies import get_currency_symbol
from .validations import validate_and_read_cli
from .load_strategy import load_strategy_from_config

msec = 1000
minute = 60 * msec
hour = 60 * minute
day = 24 * hour


class ConfigModule(object):
    raw_config: dict
    timeframe: str
    timeframe_ms: int

    @staticmethod
    async def create(args):
        config_module = ConfigModule()
        config = read_config(args.config)
        validate_and_read_cli(config, args)
        get_plot_indicators(config)

        config_module.mainplot_indicators = config["mainplot_indicators"]
        config_module.subplot_indicators = config["subplot_indicators"]
        config_module.starting_capital = float(config["starting-capital"])
        config_module.raw_config = config  # TODO remove, should be typed
        exchange_str = config["exchange"]
        config_module.timeframe = config["timeframe"]
        config_module.timeframe_ms = parse_timeframe(config_module.timeframe)
        config_module.strategy_definition = StrategyDefinition(config['strategy-name'], config['strategies-folder'])
        config_module.exchange_name = exchange_str
        config_module.exchange = create_cctx_exchange(config_module.exchange_name, config_module.timeframe)
        backtesting_till_now = config["backtesting-till-now"]
        backtesting_from = config["backtesting-from"]
        backtesting_to = config["backtesting-to"]
        config_module.backtesting_from, config_module.backtesting_to = config_from_to(config_module.exchange,
                                                                                      backtesting_from, backtesting_to,
                                                                                      backtesting_till_now)

        config_module.pairs = config["pairs"]
        config_module.btc_marketchange_ratio = await config_module.load_btc_marketchange()
        config_module.fee = config["fee"]
        config_module.stoploss = config["stoploss"]
        config_module.stoploss_type = config["stoploss-type"]
        config_module.max_open_trades = config["max-open-trades"]
        config_module.plots = config["plots"]
        config_module.roi = config["roi"]
        config_module.currency_symbol = get_currency_symbol(config_module.raw_config)
        return config_module

    async def load_btc_marketchange(self):
        print("[INFO] Fetching marketchange of BTC/USDT...")
        begin_data = await self.exchange.fetch_ohlcv(symbol='BTC/USDT', timeframe=self.timeframe,
                                                     since=self.backtesting_from, limit=1)
        end_timestamp = int(np.floor(self.backtesting_to / self.timeframe_ms) * self.timeframe_ms) - self.timeframe_ms
        end_data = await self.exchange.fetch_ohlcv(symbol='BTC/USDT', timeframe=self.timeframe, since=end_timestamp,
                                                   limit=1)

        begin_close_value = begin_data[0][4]
        end_close_value = end_data[0][4]
        return end_close_value / begin_close_value

    async def close(self):
        await self.exchange.close()


def read_config(config_path: str) -> dict:
    print(
        '======================================== \n'
        ' Starting up DemaTrading.ai BACKTESTING \n'
        '========================================')
    try:
        with open(config_path or "config.json", 'r') as configfile:
            data = configfile.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"[ERROR] No config file found at {config_path}.")
    except Exception:
        raise Exception("[ERROR] Something went wrong parsing config file.",
                        sys.exc_info()[0])
    return json.loads(data)


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


def config_from_to(exchange, backtesting_from: int, backtesting_to: int, backtesting_till_now: bool) -> tuple:
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
    return backtesting_from, backtesting_to


@asynccontextmanager
async def create_config_module(args):
    config_module = None
    try:
        config_module = await ConfigModule.create(args)
        yield config_module
    finally:
        if config_module is not None:
            await config_module.close()
