import pandas as pd
import numpy as np

from modules.stats.trade import Trade


def get_cum_profit_ratio_per_coin(signal_dict, closed_pair_trades: [Trade], fee_percentage: float,
                                  realised_drawdown=False):
    trades_opened_closed_timestamps = map_trades_to_opened_closed_timestamps(closed_pair_trades)

    values = signal_dict.values()
    df = pd.DataFrame(values).set_index("time")

    # Check if we want to calculate realised drawdown
    if realised_drawdown:
        trade_timestamps = get_trade_timestamps(closed_pair_trades)
        df = pd.concat([df, trade_timestamps], axis=1, join="inner")

    # Copy first row to zero index to save asset value before applying fees
    df = with_copied_initial_row(df)

    apply_profit_ratio(df, trades_opened_closed_timestamps)
    add_trade_fee(df, fee_percentage, trades_opened_closed_timestamps)

    df["value"] = df["profit_ratio"].cumprod()

    return df


def with_copied_initial_row(df) -> pd.DataFrame:
    head = df.head(1).copy()
    head.rename(index=lambda s: 0, inplace=True)
    return pd.concat([head, df])


def map_trades_to_opened_closed_timestamps(closed_pair_trades):
    trades_closed_opened = [(int(trade.opened_at.timestamp() * 1000), int(trade.closed_at.timestamp() * 1000)) for trade
                          in closed_pair_trades]
    return trades_closed_opened


def apply_profit_ratio(df, trades_open_closed):
    for open_timestamp, close in trades_open_closed:
        # skip the first row of each trade
        idx = np.searchsorted(df.index, open_timestamp)
        open_timestamp = df.index[max(0, idx + 1)]

        df.loc[open_timestamp: close, "profit_ratio"] = (df["close"] / df["close"].shift(1))
    df["profit_ratio"] = df["profit_ratio"].fillna(1)


def add_trade_fee(df, fee_percentage, trades_closed_opened):
    fee_ratio = 1 - fee_percentage / 100
    for opened, closed in trades_closed_opened:
        df.loc[opened, "profit_ratio"] *= fee_ratio
        df.loc[closed, "profit_ratio"] *= fee_ratio


def get_trade_timestamps(closed_pair_trades):
    trade_timestamps_list = []
    for trade in closed_pair_trades:
        trade_timestamps_list.append(int(trade.opened_at.timestamp() * 1000))
        trade_timestamps_list.append(int(trade.closed_at.timestamp() * 1000))
    trade_timestamps = pd.DataFrame(trade_timestamps_list, columns=["time"]).set_index("time")
    return trade_timestamps
