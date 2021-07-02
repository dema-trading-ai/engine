# This module contains helper functions that have to do with the config
# file, like validation and currency support

# Libraries
import json
import re
import sys
from contextlib import asynccontextmanager
from datetime import datetime
import numpy as np

# Files
from utils.utils import get_plot_indicators
from .strategy_definition import StrategyDefinition
from .cctx_adapter import create_cctx_exchange
from .currencies import get_currency_symbol
from .validations import validate_and_read_cli
from .load_strategy import load_strategy_from_config
from cli.print_utils import print_info, print_standard

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
        config_module.fee = config["fee"]
        config_module.stoploss = config["stoploss"]
        config_module.stoploss_type = config["stoploss-type"]
        config_module.max_open_trades = config["max-open-trades"]
        config_module.plots = config["plots"]
        config_module.roi = config["roi"]
        config_module.currency_symbol = get_currency_symbol(config_module.raw_config)
        return config_module

    async def close(self):
        await self.exchange.close()


def read_config(config_path: str) -> dict:
    print_standard(
        '=================================== \n'
        ' DemaTrading.ai BACKTESTING ENGINE \n'
        '===================================')
    try:
        with open(config_path or "config.json", 'r', encoding='utf-8') as configfile:
            data = configfile.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"[ERROR] No config file found at {config_path}.")
    except Exception:
        raise Exception("[ERROR] Something went wrong parsing config file.",
                        sys.exc_info()[0])
    return json.loads(data)


def print_pairs(config_json):
    pairs_string = ''.join([f'{pair} ' for pair in config_json['pairs']])
    print_info("Watching pairs: %s." % pairs_string[:-1])


def parse_timeframe(timeframe_str: str):
    print_info('Configuring timeframe...')

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
    # Configure milliseconds
    today_ms = exchange.milliseconds()
    backtesting_from_ms = exchange.parse8601("%sT00:00:00Z" % backtesting_from)
    backtesting_to_ms = exchange.parse8601("%sT00:00:00Z" % backtesting_to)

    # Get parsed dates
    backtesting_from_parsed = datetime.fromtimestamp(backtesting_from_ms / 1000.0).strftime("%Y-%m-%d")
    backtesting_to_parsed = datetime.fromtimestamp(backtesting_to_ms / 1000.0).strftime("%Y-%m-%d")

    # Define correct end date
    if backtesting_till_now or today_ms < backtesting_to_ms:
        if backtesting_till_now:
            print_info("Backtesting-till-now activated.")
        else:
            print_info("Backtesting end date extends past current date.")

        backtesting_today = datetime.fromtimestamp(today_ms / 1000.0).strftime("%Y-%m-%d")
        print_info('Changed end date %s to %s.' % (backtesting_to_parsed, backtesting_today))
        backtesting_to_ms = today_ms
        backtesting_to_parsed = backtesting_today

    # Check for incorrect configuration
    if backtesting_from_ms >= backtesting_to_ms:
        raise Exception("[ERROR] Backtesting periods are configured incorrectly.")

    print_info(f'Gathering data from {str(backtesting_from_parsed)} '
                  f'until {str(backtesting_to_parsed)}.')
    return backtesting_from_ms, backtesting_to_ms


@asynccontextmanager
async def create_config_module(args):
    config_module = None
    try:
        config_module = await ConfigModule.create(args)
        yield config_module
    finally:
        if config_module is not None:
            await config_module.close()
