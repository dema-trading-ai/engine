# Libraries
import os
import re
import sys
import requests
from pathlib import Path

from modules.stats.trade import Trade
from cli.print_utils import print_config_error

CURRENT_VERSION = "v0.7.19"

MILLISECONDS = 1000
MINUTE = 60 * MILLISECONDS
HOUR = 60 * MINUTE
DAY = 24 * HOUR


def get_project_root():
    return Path(__file__).parent.parent


def get_ohlcv_indicators() -> [str]:
    """
    :return: list with ohlcv indicator names
    """
    return ['time', 'open', 'high', 'low', 'close', 'volume', 'pair', 'buy', 'sell']


def lower_bar_to_middle_bar(s: str) -> str:
    """
    Replaces '_' with '-'
    """
    return s.replace("_", "-")


def default_empty_array_dict() -> list:
    """
    :return: list for initializing dictionary
    """
    return []


def calculate_worth_of_open_trades(open_trades: [Trade]) -> float:
    """
    Method calculates worth of open trades
    """
    return_value = 0
    for trade in open_trades:
        return_value += trade.capital
    return return_value


def get_plot_indicators(config: dict):
    config.setdefault("mainplot_indicators", ['ema5', 'ema21'])
    config.setdefault("subplot_indicators", [['volume']])


def is_running_in_docker():
    mode_env = os.getenv("RUNMODE")
    return mode_env == "docker"


def is_running_as_executable():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return True
    else:
        return False


def parse_timeframe(timeframe_str: str):
    match = re.match(r"([0-9]+)([mdh])", timeframe_str, re.I)
    if not match:
        print_config_error("Error while parsing the timeframe from config.json")
        sys.exit()
    items = re.split(r'([0-9]+)', timeframe_str)
    if items[2] == 'm':
        timeframe_time = int(items[1]) * MINUTE
    elif items[2] == 'h':
        timeframe_time = int(items[1]) * HOUR
    else:
        print_config_error("Error while parsing the timeframe from config.json")
        sys.exit()
    return timeframe_time


def check_internet_connection() -> bool:
    try:
        requests.get("https://google.com", timeout=5)
        return True

    except (requests.ConnectionError, requests.Timeout):
        return False
