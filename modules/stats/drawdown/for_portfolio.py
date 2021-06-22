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
    df = pd.DataFrame.from_dict(realised_profits_per_timestamp, columns=['value'], orient='index')
    df["drawdown"] = df["value"] / df["value"].cummax()

    max_realised_drawdown = df["drawdown"].min()

    return max_realised_drawdown
