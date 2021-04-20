# Libraries
from pathlib import Path
from collections import defaultdict
from pandas import DataFrame
import pandas as pd
import rapidjson
from datetime import datetime
import plotly.graph_objects as go

CURRENT_VERSION = "v0.3.1"


def get_project_root():
    return Path(__file__).parent


def lower_bar_to_middle_bar(s: str) -> str:
    """Replaces '_' with '-' """
    return s.replace("_", "-")

  
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
    df.index = df.index.map(str)
    return df.to_dict('index')


def dict_to_df(data: dict, indicators: list) -> DataFrame:
    """
    Method turns dictionary into dataframe
    :param data: json with OHLCV data
    :type data: json
    :return: dataframe with OHLCV data
    :rtype: DataFrame
    """
    json_file = rapidjson.loads(data)
    df = pd.DataFrame.from_dict(json_file, orient='index', columns=indicators)
    df.index = df.index.map(int)
    return df

  
def plot_dataframe(pair: str, df: DataFrame, indicator: str):
    """
    Plot dataframe of a certain coin pair with given indicator
    :param pair: Certain coin pair in "AAA/BBB" format
    :type pair: string
    :param df: Downloaded data to write to the datafile
    :type df: DataFrame
    :param indicator: certain indicator to plot
    :type indicator: string
    :return: None
    :rtype: None
    """

    dates = [datetime.fromtimestamp(time / 1000) for time in df["time"]]

    fig = go.Figure(data=go.Ohlc(x=dates,
                                 open=df["open"],
                                 high=df["high"],
                                 low=df["low"],
                                 close=df["close"],
                                 name='OHLC'))

    fig.add_trace(go.Scatter(x=dates, y=df[indicator], name=indicator, line=dict(color='royalblue', width=2, dash='dot')))

    fig.update_layout(
        title='OHLC Chart',
        yaxis_title=pair)

    fig.show()
    fig.write_html("data/backtesting-data/binance/plot%s.html" % pair.replace("/", ""))


