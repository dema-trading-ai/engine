# Libraries
from pathlib import Path
from collections import defaultdict
from pandas import DataFrame
import pandas as pd
import rapidjson


def get_project_root():
    return Path(__file__).parent

def default_empty_array_dict() -> list:
    """
    :return: list for initializing dictionary
    :rtype: List.
    """
    return []

def default_empty_dict_dict() -> dict:
    """
    :return: Dictionary for initializing default dictionary
    :rtype: Dict.
    """
    return defaultdict(int)

def calculate_worth_of_open_trades(open_trades) -> float:
    """
    Method calculates worth of open trades
    :param open_trades: array of open trades
    :type open_trades: [Trade]
    :return: returns the total value of all open trades
    :rtype: float.
    """
    return_value = 0
    for trade in open_trades:
        return_value += (trade.currency_amount * trade.current)
    return return_value

def df_to_dict(df: DataFrame) -> dict:
    """
    Method turns dataframe into dictionary
    :param df: dataframe with OHLCV data
    :type df: DataFrame
    :return: dictionary with OHLCV data
    :rtype: dict
    """
    df_dict = {}
    for row in df.iterrows():
        df_json = row[1].to_dict()
        df_dict[str(df_json['time'])] = df_json
    return df_dict

def dict_to_df(data: dict, indicators: list) -> DataFrame:
    """
    Method turns dictionary into dataframe
    :param data: json with OHLCV data
    :type data: json
    :return: dataframe with OHLCV data
    :rtype: DataFrame
    """
    json_file = rapidjson.loads(data)
    ohlcv_dict = {int(tick): list(json_file[tick].values()) for tick in json_file}
    df = DataFrame.from_dict(ohlcv_dict, orient='index', columns=indicators)
    df.index = pd.to_datetime(df.index, unit='ms')
    df.sort_index(inplace=True)
    return df
