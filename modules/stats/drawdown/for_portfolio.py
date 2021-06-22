import pandas as pd


def get_max_seen_drawdown_for_portfolio(capital_per_timestamp: dict):
    max_seen_drawdown = {}

    df = pd.DataFrame.from_dict(capital_per_timestamp, columns=['value'], orient='index')
    df["drawdown"] = df["value"] / df["value"].cummax()

    max_seen_drawdown["drawdown"] = df["drawdown"].min()
    max_seen_drawdown["at"] = df["drawdown"].idxmin()
    max_seen_drawdown["from"] = df.loc[:max_seen_drawdown["at"]].value.idxmax()

    df_top_slice = df.loc[max_seen_drawdown["at"]:]
    df_next_peak = df_top_slice.loc[df_top_slice["drawdown"] == 0]

    if len(df_next_peak) > 0:
        max_seen_drawdown["to"] = df_next_peak.index[0]
    else:
        max_seen_drawdown["to"] = 0

    return max_seen_drawdown


def get_max_realised_drawdown_for_portfolio(realised_profits_per_timestamp: dict):
    max_realised_drawdown = {
        "drawdown": 1.0,  # ratio
        "max_consecutive_losses": 0,
        "losing_trades": 0
    }

    df = pd.DataFrame.from_dict(realised_profits_per_timestamp, columns=['value'], orient='index')
    df["drawdown"] = (df["value"] - df["value"].cummax()) / df["value"].cummax()
    df['losing_trade'] = df.value.lt(df.value.shift())

    df['consecutive_losses'] = df.losing_trade.cumsum()-df.losing_trade.cumsum().where(~df.losing_trade)\
        .ffill()\
        .fillna(0)\
        .astype(int)

    max_realised_drawdown['drawdown'] = df["drawdown"].min()
    losing_trades_count = df["losing_trade"].value_counts()
    if True in losing_trades_count:
        max_realised_drawdown['losing_trades'] = losing_trades_count.loc[True]
    else:
        max_realised_drawdown['losing_trades'] = 0
    max_realised_drawdown['max_consecutive_losses'] = df["consecutive_losses"].max()

    return max_realised_drawdown
