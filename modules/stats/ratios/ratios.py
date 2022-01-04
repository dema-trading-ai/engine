import pandas as pd
import numpy as np

from typing import Optional


def compute_sharpe_ratio(df: pd.DataFrame) -> Optional[float]:
    expected_excess_asset_return = np.subtract(df['returns'], df['risk_free'])
    sharpe_ratio_per_timestamp = np.divide(expected_excess_asset_return, np.std(expected_excess_asset_return))

    if not np.isnan(sharpe_ratio_per_timestamp).all() and not np.isinf(sharpe_ratio_per_timestamp[1:]).all():
        sharpe_ratio = float(np.mean(sharpe_ratio_per_timestamp))

    else:
        sharpe_ratio = None

    return sharpe_ratio


def compute_sortino_ratio(df: pd.DataFrame) -> Optional[float]:

    average_realized_return = np.mean(df['returns'])
    additional_return = average_realized_return - df['risk_free'][0]

    df['down_dev'] = np.where(df['returns'] < 0, abs(df['returns']) ** 2, 0)
    average_squared_downside_deviation = np.mean(df['down_dev'])
    target_downside_deviation = np.sqrt(average_squared_downside_deviation)

    if target_downside_deviation > 0:
        sortino_ratio = additional_return / target_downside_deviation

    else:
        sortino_ratio = None

    return sortino_ratio
