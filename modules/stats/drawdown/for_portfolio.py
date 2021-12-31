import pandas as pd
from datetime import timedelta

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
    df = utils.convert_dict_to_dataframe(realised_profits_per_timestamp)

    df['timestamps'] = df.index

    df['returns'] = df['capital'] - df['capital'].shift()
    df['timesteps'] = df['timestamps'] - df['timestamps'].shift()

    df['negative_returns_timesteps'] = df.loc[df['returns'] < 0, ['timesteps']]  # Keep only the timesteps with negative returns

    longest_realised_drawdown = df['negative_returns_timesteps'].max()

    return longest_realised_drawdown


def get_longest_seen_drawdown(capital_per_timestamp: dict) -> timedelta:

    # TODO: Check if first (from highest to lowest cap) or second (longest consecutive negative returns) is the correct solution

    df = utils.convert_dict_to_dataframe(capital_per_timestamp)

    start_drawdown = df['capital'].idxmax()

    end_drawdown = df['capital'].idxmin()

    longest_seen_drawdown = end_drawdown - start_drawdown

    # df['negative_returns_timesteps'] = df.loc[
    #     df['returns'] < 0, ['timesteps']]  # Keep only the timesteps with negative returns
    #
    # df['consecutive_negative_returns_timesteps'] = df['negative_returns_timesteps'].groupby(
    #     (df['negative_returns_timesteps'] != df['negative_returns_timesteps'].shift()).cumsum()).transform(
    #     'size')  # Count consecutive timesteps with negative returns
    #
    # longest_seen_drawdown = df['consecutive_negative_returns_timesteps'].max() * df['timesteps'].iloc[
    #     1]  # Use second row as first is NaT

    return longest_seen_drawdown
