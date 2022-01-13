from datetime import timedelta
from typing import Tuple, Optional

from modules.setup.config.validations import validate_ratios
from modules.stats.ratios import utils, ratios


def get_sharpe_sortino_ratios(capital_per_timestamp: dict, risk_free: float = 0.0) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
    df = utils.change_capital_dict_to_dataframe(capital_per_timestamp, risk_free)

    ninety_d, three_y = validate_ratios(df)

    df_90_d = df.truncate(after=df.index[0] + timedelta(days=90)) if ninety_d else df
    sharpe_90_d = ratios.compute_sharpe_ratio(df_90_d)
    sortino_90_d = ratios.compute_sortino_ratio(df_90_d)

    df_3_y = df.truncate(after=df.index[0] + timedelta(days=3 * 365)) if three_y else df  # Does not take leap years into account
    sharpe_3_y = ratios.compute_sharpe_ratio(df_3_y)
    sortino_3_y = ratios.compute_sortino_ratio(df_3_y)

    return sharpe_90_d, sortino_90_d, sharpe_3_y, sortino_3_y
