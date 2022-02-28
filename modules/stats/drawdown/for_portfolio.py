from datetime import timedelta
from typing import Dict, Union

import pandas as pd

from modules.stats import utils
from modules.stats.drawdown.drawdown import get_max_drawdown_ratio, compute_drawdown_lengths


def get_max_seen_drawdown_for_portfolio(capital_per_timestamp: dict):
    max_seen_drawdown = {}

    df = pd.DataFrame.from_dict(capital_per_timestamp, columns=['value'], orient='index')
    df["drawdown"] = df["value"] / df["value"].cummax()

    max_seen_drawdown["drawdown"] = df["drawdown"].min() - 1
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

    return max_realised_drawdown - 1


def get_longest_drawdown(per_timestamp_dict: dict) -> Dict[str, Union[timedelta, bool]]:
    """
    Takes a dictionary representing chronological movements of funds and returns a dictionary with the length of the
    longest drawdown within those movements and whether this longest drawdown is ongoing
    :param per_timestamp_dict: Can be either capital or realised profits
    :return: A dictionary containing the length of the longest drawdown and whether the longest drawdown is ongoing
    """

    df = utils.convert_timestamp_dict_to_dataframe(per_timestamp_dict)

    longest_drawdown, last_drawdown = compute_drawdown_lengths(df)

    # Checks if the longest drawdown was actually computed
    if longest_drawdown == timedelta(0) and last_drawdown == timedelta(0):
        is_ongoing = False

    else:
        is_ongoing = longest_drawdown == last_drawdown

    drawdown_info = {
        'longest_drawdown': longest_drawdown,
        'is_ongoing': is_ongoing
    }

    return drawdown_info
