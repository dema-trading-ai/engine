import numpy as np
import pandas as pd
from datetime import timedelta
from typing import Tuple

from modules.stats.drawdown.drawdown import get_max_drawdown_ratio
from modules.stats import utils


def get_max_seen_drawdown_for_portfolio(capital_per_timestamp: dict):
    max_seen_drawdown = {}

    df = pd.DataFrame.from_dict(capital_per_timestamp, columns=['value'], orient='index')
    df["drawdown"] = df["value"] / df["value"].cummax()

    max_seen_drawdown["drawdown"] = df["drawdown"].min()
    max_seen_drawdown["at"] = df["drawdown"].idxmin()
    max_seen_drawdown["from"] = df.loc[:max_seen_drawdown["at"]].value.idxmax()
    df_after_max_drawdown = df.loc[max_seen_drawdown["at"]:]
    df_after_recovery = df_after_max_drawdown.loc[df_after_max_drawdown["drawdown"] == 1]

    if len(df_after_recovery) > 0:
        max_seen_drawdown["to"] = df_after_recovery.index[0]
    else:
        max_seen_drawdown["to"] = 0

    # if drawdown is from the very first timestep
    if max_seen_drawdown["from"] == 0:
        max_seen_drawdown["from"] = df.index[1]

    return max_seen_drawdown


def get_max_realised_drawdown_for_portfolio(realised_profits_per_timestamp: dict):
    df = pd.DataFrame.from_dict(realised_profits_per_timestamp, columns=['value'], orient='index')
    max_realised_drawdown = get_max_drawdown_ratio(df)

    return max_realised_drawdown


def get_longest_realised_drawdown(realised_profits_per_timestamp: dict) -> timedelta:
    df = utils.convert_timestamp_dict_to_dataframe(realised_profits_per_timestamp)

    df['timestamps'] = df.index

    df['returns'] = df['capital'] - df['capital'].shift()
    df['timesteps'] = df['timestamps'] - df['timestamps'].shift()

    df['negative_returns_timesteps'] = df.loc[
        df['returns'] < 0, ['timesteps']]  # Keep only the timesteps with negative returns

    longest_realised_drawdown = df['negative_returns_timesteps'].max()

    return longest_realised_drawdown


def get_longest_seen_drawdown(capital_per_timestamp: dict) -> Tuple[timedelta, bool]:
    df = utils.convert_timestamp_dict_to_dataframe(capital_per_timestamp)

    # Track highest capital, downward, and upward trends
    df['max_capital'] = df['capital'].cummax()  # Tracks the highest capital chronologically

    df['down_trend'] = np.where(df['capital'] < df['capital'].shift(), 1, 0)
    df['down_trend'] = df['down_trend'].shift(-1)  # Shift the downward trend as we look at when the trend is about to go down

    df['up_trend'] = np.where(df['capital'] > df['capital'].shift(), 1, 0)

    # Track start and end of drawdowns
    df['start_drawdown'] = np.where((df['max_capital'] == df['capital']) & (df['down_trend'] == 1), 1, 0)
    df['end_drawdown'] = np.where((df['max_capital'] == df['capital']) & (df['up_trend'] == 1), 1, 0)

    last_row = df.iloc[-1]  # Save the last row to compute whether the longest drawdown is ongoing

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

    longest_seen_drawdown = df['length_drawdown'].max()

    is_ongoing = longest_seen_drawdown == df['length_drawdown'].iloc[-1]

    return longest_seen_drawdown, is_ongoing
