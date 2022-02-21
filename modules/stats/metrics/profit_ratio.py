from datetime import datetime

import numpy as np
import pandas as pd
from pandas import DataFrame

from modules.stats.trade import Trade, SellReason


def get_seen_cum_profit_ratio(signal_dict, closed_trades: [Trade], fee_percentage: float):
    df = pd.DataFrame(signal_dict.values()).set_index("time")
    return get_profit_ratio(df, fee_percentage, closed_trades)


def get_realised_profit_ratio(signal_dict, closed_trades: [Trade], fee_percentage: float):
    df = pd.DataFrame(signal_dict.values()).set_index("time")
    trade_timestamps = get_trade_timestamps(closed_trades)
    df = pd.concat([df, trade_timestamps], axis=1, join="inner")
    return get_profit_ratio(df, fee_percentage, closed_trades)


def correct_for_stoploss_roi(df, closed_trades):
    df["corrected_close"] = df["close"]
    for trade in closed_trades:
        if trade.sell_reason == SellReason.ROI or trade.sell_reason == SellReason.STOPLOSS:
            df.loc[datetime.timestamp(trade.closed_at) * 1000, "corrected_close"] = trade.close
    return df


def get_profit_ratio(df, fee_percentage, closed_trades):
    trades_opened_closed_timestamps = map_trades_to_opened_closed_timestamps(closed_trades)
    # Copy first row to zero index to save asset value before applying fees
    df = with_copied_initial_row(df)
    df = correct_for_stoploss_roi(df, closed_trades)
    df = apply_profit_ratio(df, trades_opened_closed_timestamps)
    df = add_trade_fee(df, fee_percentage, trades_opened_closed_timestamps)
    df["value"] = df["profit_ratio"].cumprod()
    return df


def get_profit_ratio_from_capital(capital: dict):
    df = DataFrame(capital.items(), columns=['time', 'capital']).set_index('time')
    df["profit_ratio"] = df["capital"] / df["capital"].shift(1)
    df.loc[df.index[0], "profit_ratio"] = 1
    df["value"] = df["profit_ratio"].cumprod()
    return df


def with_copied_initial_row(df: DataFrame) -> pd.DataFrame:
    if len(df.index) < 2:
        # not enough data, skip
        return df
    time_difference = df.index[1] - df.index[0]
    timestep_before_start = df.index[0] - time_difference
    head = df.head(1).copy()
    head.rename(index=lambda s: timestep_before_start, inplace=True)
    return pd.concat([head, df])


def map_trades_to_opened_closed_timestamps(closed_trades):
    trades_closed_opened = [(int(trade.opened_at.timestamp() * 1000), int(trade.closed_at.timestamp() * 1000)) for trade
                            in closed_trades]
    return trades_closed_opened


def apply_profit_ratio(df, trades_open_closed):
    df["corrected_close"] = df["corrected_close"].fillna(value=None, method='ffill')
    df["profit_ratio"] = None
    for open_timestamp, close in trades_open_closed:
        # skip the first row of each trade
        idx = np.searchsorted(df.index, open_timestamp)
        open_timestamp = df.index[max(0, idx + 1)]

        df.loc[open_timestamp: close, "profit_ratio"] = (df["corrected_close"] / df["corrected_close"].shift(1))
    df["profit_ratio"] = df["profit_ratio"].fillna(value=1)
    return df


def add_trade_fee(df, fee_percentage, trades_closed_opened):
    fee_ratio = 1 - fee_percentage / 100
    for opened, closed in trades_closed_opened:
        df.loc[opened, "profit_ratio"] *= fee_ratio
        df.loc[closed, "profit_ratio"] *= fee_ratio
    return df


def get_trade_timestamps(closed_trades):
    trade_timestamps_list = []
    for trade in closed_trades:
        trade_timestamps_list.append(int(trade.opened_at.timestamp() * 1000))
        trade_timestamps_list.append(int(trade.closed_at.timestamp() * 1000))
    trade_timestamps = pd.DataFrame(trade_timestamps_list, columns=["time"]).set_index("time")
    return trade_timestamps
