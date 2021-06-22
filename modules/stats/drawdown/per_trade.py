import pandas as pd

from modules.stats.drawdown.drawdown import get_max_drawdown_ratio
from modules.stats.trade import Trade


def get_max_seen_drawdown_per_trade(signal_dict, trade: Trade, fee_percentage: float):

    values = signal_dict.values()
    df = pd.DataFrame(values).set_index("time")

    # Copy first row to zero index to save asset value before applying fees
    df = with_copied_initial_row(df)

    opened_at_timestamp = int(trade.opened_at.timestamp() * 1000)

    apply_profit_ratio(df, opened_at_timestamp)
    add_trade_fee(df, fee_percentage, opened_at_timestamp)

    df["value"] = df["profit_ratio"].cumprod()

    return get_max_drawdown_ratio(df)


def with_copied_initial_row(df) -> pd.DataFrame:
    head = df.head(1).copy()
    head.rename(index=lambda s: 0, inplace=True)
    return pd.concat([head, df])


def apply_profit_ratio(df, open_timestamp):
    df.loc[open_timestamp:, "profit_ratio"] = (df["close"] / df["close"].shift(1))
    df["profit_ratio"] = df["profit_ratio"].fillna(1)


def add_trade_fee(df, fee_percentage, open):
    fee_ratio = 1 - fee_percentage / 100
    df.loc[open, "profit_ratio"] *= fee_ratio
