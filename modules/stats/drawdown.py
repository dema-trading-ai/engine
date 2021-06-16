import pandas as pd


def get_max_seen_drawdown(signal_dict, closed_pair_trades, fee_percentage: float):
    trades_closed_open = get_open_close(closed_pair_trades)

    df = get_inposition_df(trades_closed_open, signal_dict)
    df["change"] = (df["close"] / df["close"].shift(-1))

    for open, close in trades_closed_open:
        df.loc[open, "change"] *= fee_percentage
        df.loc[close, "change"] *= fee_percentage

    df["value"] = df[df["in_position"] == 1]["change"].cumprod()
    return get_drawdown(df)


def get_drawdown(df):
    cummax = df["cumprod"].cummax()
    df["drawdown"] = (df["cumprod"] - cummax) / cummax
    return df["drawdown"].min()


def get_inposition_df(trades_closed_open, signal_dict):
    values = signal_dict.values()
    df = pd.DataFrame(values).set_index("time")
    df["in_position"] = 0

    for open, close in trades_closed_open:
        df.loc[open: close]["in_position"] = 1

    return df


def get_open_close(closed_pair_trades):
    trades_closed_open = [(int(trade.opened_at.timestamp() * 1000), int(trade.closed_at.timestamp() * 1000)) for trade
                          in closed_pair_trades]
    return trades_closed_open
