# Libraries
import os
from pathlib import Path
from typing import Literal
from pandas import DataFrame
import pandas as pd
import rapidjson
import re

from modules.stats.trade import Trade

CURRENT_VERSION = "v0.7.1"

msec = 1000
minute = 60 * msec
hour = 60 * minute
day = 24 * hour


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


def df_to_dict(df: DataFrame) -> dict:
    """
    Method turns dataframe into dictionary
    """
    df.index = df.index.map(str)
    return df.to_dict('index')


def str_to_df(data: str) -> DataFrame:
    """
    Method turns dictionary into dataframe
    """
    indicators = get_ohlcv_indicators()
    json_file = rapidjson.loads(data)
    df = pd.DataFrame.from_dict(json_file, orient='index', columns=indicators)
    df.index = df.index.map(int)
    return df


def get_plot_indicators(config: dict):
    config.setdefault("mainplot_indicators", ['ema5', 'ema21'])
    config.setdefault("subplot_indicators", ['volume'])


def is_running_in_docker():
    mode_env = os.getenv("RUNMODE")
    return mode_env == "docker"


def get_verbosity():
    return os.getenv("VERBOSITY") or "none"


def is_verbosity(verbosity: Literal["debug", "none"]):
    return get_verbosity() == verbosity


def parse_timeframe(timeframe_str: str):
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
