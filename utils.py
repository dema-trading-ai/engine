# Libraries
from pathlib import Path
from collections import defaultdict
from pandas import DataFrame
import pandas as pd
import rapidjson

# Files
from models.trade import Trade

CURRENT_VERSION = "v0.4.1"


def get_project_root():
    return Path(__file__).parent


def get_ohlcv_indicators() -> [str]:
    """
    :return: list with ohlcv indicator names
    :rtype: list
    """
    return ['time', 'open', 'high', 'low', 'close', 'volume', 'pair', 'buy', 'sell']


def lower_bar_to_middle_bar(s: str) -> str:
    """
    Replaces '_' with '-'
    :param s: string that needs to be changed
    :type s: string
    :return: changed string
    :rtype: string
    """
    return s.replace("_", "-")

  
def default_empty_array_dict() -> list:
    """
    :return: list for initializing dictionary
    :rtype: list
    """
    return []


def default_empty_dict_dict() -> dict:
    """
    :return: dictionary for initializing default dictionary
    :rtype: dict
    """
    return defaultdict(int)


def calculate_worth_of_open_trades(open_trades: [Trade]) -> float:
    """
    Method calculates worth of open trades
    :param open_trades: array of open trades
    :type open_trades: [Trade]
    :return: returns the total value of all open trades
    :rtype: float
    """
    return_value = 0
    for trade in open_trades:
        return_value += trade.capital
    return return_value


def df_to_dict(df: DataFrame) -> dict:
    """
    Method turns dataframe into dictionary
    :param df: dataframe with OHLCV data
    :type df: DataFrame
    :return: dictionary with OHLCV data
    :rtype: dict
    """
    df.index = df.index.map(str)
    return df.to_dict('index')

def dict_to_df(data: dict) -> DataFrame:
    """
    Method turns dictionary into dataframe
    :param data: json with OHLCV data
    :type data: json
    :return: dataframe with OHLCV data
    :rtype: DataFrame
    """
    indicators = get_ohlcv_indicators()
    json_file = rapidjson.loads(data)
    df = pd.DataFrame.from_dict(json_file, orient='index', columns=indicators)
    df.index = df.index.map(int)
    return df
