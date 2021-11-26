import numpy as np
import pandas as pd

from modules.stats.drawdown.drawdown import get_max_drawdown_ratio
from modules.setup.config.validations import validate_sharpe_ratio


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


def convert_dataframe(capital_per_timestamp: dict) -> pd.DataFrame:
    df = pd.DataFrame.from_dict(capital_per_timestamp, columns=['value'], orient='index')

    if str(type(df.index.dtype)) == "<class 'numpy.dtype[float64]'>":  # Check if a test is happening
        df = df.iloc[1:, :]
        df.index = pd.to_datetime(df.index, unit='ms')
        df = df.resample('D').apply(lambda x: x.iloc[-1])

    return df


def get_sharpe_ratio(capital_per_timestamp: dict, risk_free: int = 0) -> str:
    df = convert_dataframe(capital_per_timestamp)
    df['returns'] = (df['value'] - df['value'].shift()) / 100
    df = df.iloc[1:, :]
    df['rf'] = risk_free

    expected_excess_asset_return = np.subtract(df['returns'], df['rf'])
    sharpe_ratio_per_timestamp = np.divide(expected_excess_asset_return, np.std(expected_excess_asset_return))
    avg_sharpe_ratio = np.mean(sharpe_ratio_per_timestamp)

    final_ratio = validate_sharpe_ratio(str(avg_sharpe_ratio))

    return final_ratio
