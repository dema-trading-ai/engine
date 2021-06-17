import pandas as pd

from modules.stats.drawdown.drawdown import get_max_drawdown_ratio
from modules.stats.trade import Trade


def get_max_seen_drawdown_per_coin(signal_dict, closed_pair_trades: [Trade], fee_percentage: float):
    trades_open_closed = trade_to_open_close(closed_pair_trades)

    values = signal_dict.values()
    df = pd.DataFrame(values).set_index("time")

    apply_worth_change(df, trades_open_closed)
    apply_fee_at_position_changed(df, fee_percentage, trades_open_closed)

    df["value"] = df["worth_change"].cumprod()

    return get_max_drawdown_ratio(df)


def trade_to_open_close(closed_pair_trades):
    trades_closed_open = [(int(trade.opened_at.timestamp() * 1000), int(trade.closed_at.timestamp() * 1000)) for trade
                          in closed_pair_trades]
    return trades_closed_open


def apply_worth_change(df, trades_open_closed):
    df["worth_change"] = 1
    for open, close in trades_open_closed:
        df.loc[open: close, "worth_change"] = (df["close"] / df["close"].shift(-1))


def apply_fee_at_position_changed(df, fee_percentage, trades_closed_open):
    fee_ratio = 1 - fee_percentage / 100
    for open, close in trades_closed_open:
        df.loc[open, "worth_change"] *= fee_ratio
        df.loc[close, "worth_change"] *= fee_ratio
