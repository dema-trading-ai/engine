import numpy as np
import pandas as pd

from cli.print_utils import print_warning
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


def convert_dataframe(capital_per_timestamp: dict, risk_free: float) -> pd.DataFrame:
    """
    Converts a dict of capital per timestamps to a dataframe with timestamps as index, and with a daily returns column
    """

    df = pd.DataFrame.from_dict(capital_per_timestamp, columns=['value'], orient='index')

    first_value = df['value'][0]
    df = df.iloc[1:, :]

    df.index = pd.to_datetime(df.index, unit='ms')
    df = df.resample('D').apply(lambda x: x.iloc[-1])

    df.loc[df.index[0]] = first_value  # Replace with previous first value to include price of first buy in returns
    df = df.sort_index()

    df['returns'] = (df['value'] - df['value'].shift()) / 100
    df['rf'] = risk_free

    return df


def get_sharpe_ratio(capital_per_timestamp: dict, risk_free: float = 0.0) -> float:
    df = convert_dataframe(capital_per_timestamp, risk_free)

    if (df['returns'] == 0.0).all():
        print_warning('Unable to compute ratios: No trades were made')

    if len(df['value']) < 2:
        print_warning('Unable to compute ratios: The backtesting period needs to be at least 24h')

    expected_excess_asset_return = np.subtract(df['returns'], df['rf'])
    sharpe_ratio_per_timestamp = np.divide(expected_excess_asset_return, np.std(expected_excess_asset_return))

    avg_sharpe_ratio = float(np.mean(sharpe_ratio_per_timestamp))

    return avg_sharpe_ratio


def get_sortino_ratio(capital_per_timestamp: dict, risk_free: float = 0.0) -> float:
    df = convert_dataframe(capital_per_timestamp, risk_free)

    average_realized_return = np.mean(df['returns'])
    additional_return = average_realized_return - risk_free

    df['down_dev'] = np.where(df['returns'] < 0, abs(df['returns']) ** 2, 0)
    average_squared_downside_deviation = np.mean(df['down_dev'])
    target_downside_deviation = np.sqrt(average_squared_downside_deviation)

    sortino_ratio = additional_return / target_downside_deviation

    return sortino_ratio
