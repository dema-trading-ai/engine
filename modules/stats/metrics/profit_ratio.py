from datetime import datetime

import pandas as pd
import numpy as np

from modules.stats.trade import Trade, SellReason


def get_seen_cum_profit_ratio_per_coin(signal_dict, closed_pair_trades: [Trade], fee_percentage: float):
    df = pd.DataFrame(signal_dict.values()).set_index("time")
    return get_profit_ratio(df, fee_percentage, closed_pair_trades)


def get_realised_profit_ratio(signal_dict, closed_pair_trades: [Trade], fee_percentage: float):
    df = pd.DataFrame(signal_dict.values()).set_index("time")
    trade_timestamps = get_trade_timestamps(closed_pair_trades)
    df = pd.concat([df, trade_timestamps], axis=1, join="inner")
    return get_profit_ratio(df, fee_percentage, closed_pair_trades)


def correct_for_stoploss_roi(df, closed_pair_trades):
    df["corrected_close"] = df["close"]
    for trade in closed_pair_trades:
        if trade.sell_reason == SellReason.ROI or trade.sell_reason == SellReason.STOPLOSS:
            df.loc[datetime.timestamp(trade.closed_at) * 1000, "corrected_close"] = trade.close


def get_profit_ratio(df, fee_percentage, closed_pair_trades):
    trades_opened_closed_timestamps = map_trades_to_opened_closed_timestamps(closed_pair_trades)
    # Copy first row to zero index to save asset value before applying fees
    df = with_copied_initial_row(df)
    correct_for_stoploss_roi(df, closed_pair_trades)
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
    df["corrected_close"] = df["corrected_close"].fillna(value=None, method='ffill')
    for open_timestamp, close in trades_open_closed:
        # skip the first row of each trade
        idx = np.searchsorted(df.index, open_timestamp)
        open_timestamp = df.index[max(0, idx + 1)]

        df.loc[open_timestamp: close, "profit_ratio"] = (df["corrected_close"] / df["corrected_close"].shift(1))
    df["profit_ratio"] = df["profit_ratio"].fillna(value=1)


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
