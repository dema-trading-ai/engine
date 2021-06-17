import pandas as pd

from modules.stats.drawdown.drawdown import get_max_drawdown_ratio
from modules.stats.trade import Trade


def get_max_seen_drawdown_per_trade(signal_dict, trade: Trade, fee_percentage: float):

    values = signal_dict.values()
    df = pd.DataFrame(values).set_index("time")

    # Copy first row to zero index to save asset value before applying fees
    df = with_copied_initial_row(df)

    open = int(trade.opened_at.timestamp() * 1000)

    apply_worth_change(df, open)
    apply_fee_at_position_changed(df, fee_percentage, open)

    df["value"] = df["worth_change"].cumprod()

    return get_max_drawdown_ratio(df)


def with_copied_initial_row(df) -> pd.DataFrame:
    head = df.head(1).copy()
    head.rename(index=lambda s: 0, inplace=True)
    return pd.concat([head, df])


def apply_worth_change(df, open):
    df.loc[open:, "worth_change"] = (df["close"] / df["close"].shift(1))
    df["worth_change"] = df["worth_change"].fillna(1)


def apply_fee_at_position_changed(df, fee_percentage, open):
    fee_ratio = 1 - fee_percentage / 100
    df.loc[open, "worth_change"] *= fee_ratio
