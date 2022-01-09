import pandas as pd
import numpy as np
from datetime import timedelta
from typing import Tuple


def get_max_drawdown_ratio(df: pd.DataFrame):
    """
    @param df: with column["value"]
    """
    df["drawdown_ratio"] = df["value"] / df["value"].cummax()
    return df["drawdown_ratio"].min()


def get_max_drawdown_ratio_without_buy_rows(df: pd.DataFrame):
    """
    @param df: with column["value"]
    """
    df["drawdown_ratio"] = df["value"] / df["value"].cummax()
    ans = df.loc[df['buy'] == 0.0]["drawdown_ratio"].min()
    return ans


def get_max_drawdown_ratio_series(series: pd.Series):
    series = series / series.cummax()
    return series.min()


def compute_drawdown_lengths(df: pd.DataFrame) -> Tuple[timedelta, timedelta]:
    """
    Takes a dataframe and computes all drawdowns and their respective lengths
    :param df: The dataframe with all movements to be computed
    :return: A tuple containing the longest drawdown and the last drawdown. The last drawdown is used to determine
    whether the longest drawdown is ongoing.
    """

    # Track the highest capital, downward, and upward trends
    df['max_capital'] = df['capital'].cummax()

    df['down_trend'] = np.where(df['capital'] < df['capital'].shift(), 1, 0)
    df['down_trend'] = df['down_trend'].shift(-1)  # Shift the downward trend as we look at when the trend is about
    # to go down

    df['up_trend'] = np.where(df['capital'] > df['capital'].shift(), 1, 0)

    # Track start and end of drawdowns
    df['start_drawdown'] = np.where((df['max_capital'] == df['capital']) & (df['down_trend'] == 1), 1, 0)
    df['end_drawdown'] = np.where((df['max_capital'] == df['capital']) & (df['up_trend'] == 1), 1, 0)

    last_row = df.iloc[-1]  # Save the last row to compute the last drawdown

    df = df.drop(
        df[  # Remove rows that do not indicate the start or the end of a drawdown
            (df['start_drawdown'] == 0) & (df['end_drawdown'] == 0) |
            (  # Remove superfluous drawdown start and end indicators
                    (df['end_drawdown'] == 1) &
                    (df['start_drawdown'] == 0) &
                    (df['end_drawdown'].shift() == 1) &
                    (df['start_drawdown'].shift() == 0)
            )
            ].index
    )

    df = df.append(last_row)

    # Compute every drawdown length
    df['timestamps'] = df.index
    df['length_drawdown'] = df['timestamps'] - df['timestamps'].shift()

    longest_drawdown = df['length_drawdown'].max()
    last_drawdown = df['length_drawdown'].iloc[-1]

    return longest_drawdown, last_drawdown
