import numpy as np
import pandas as pd

from modules.stats.drawdown.drawdown import get_max_drawdown_ratio


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


def convert_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop(labels=0)
    df.index = pd.to_datetime(df.index, unit='ms')
    convert_df = df.resample('D').sum()
    return convert_df


def get_sharpe_ratio(capital_per_timestamp: dict) -> float:
    df = pd.DataFrame.from_dict(capital_per_timestamp, columns=['value'], orient='index')
    convert_df = convert_dataframe(df) if df['value'].iloc[0] != 100.0 else df.drop(labels=0)
    convert_df['returns'] = (convert_df['value'] - convert_df['value'].shift()) / 100
    mean_rx = convert_df['returns'].sum() / (len(convert_df['returns']) - 1)
    rf = 0
    std_dev = np.std(convert_df['returns'])
    sharpe_ratio = (mean_rx - rf) / std_dev
    return sharpe_ratio
