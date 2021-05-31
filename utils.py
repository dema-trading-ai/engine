# Libraries
from pathlib import Path
from pandas import DataFrame
import pandas as pd
import rapidjson

from modules.stats.trade import Trade

CURRENT_VERSION = "v0.6.3"


def get_project_root():
    return Path(__file__).parent


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


def dict_to_df(data: str) -> DataFrame:
    """
    Method turns dictionary into dataframe
    """
    indicators = get_ohlcv_indicators()
    json_file = rapidjson.loads(data)
    df = pd.DataFrame.from_dict(json_file, orient='index', columns=indicators)
    df.index = df.index.map(int)
    return df


def get_plot_indicators(config):
    """
    Method that initializes indicators
    :param config: main configuration
    :type config: dict
    :return: None
    :rtype: None
    """

    config.setdefault("mainplot_indicators", ['ema5', 'ema21'])
    config.setdefault("subplot_indicators", ['volume'])
