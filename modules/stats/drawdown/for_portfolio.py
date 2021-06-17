import pandas as pd


def get_max_seen_drawdown_for_portfolio(capital_per_timestamp: dict):
    df = pd.DataFrame.from_dict(capital_per_timestamp, columns=['value'], orient='index')
    df["drawdown"] = (df["value"] - df["value"].cummax()) / df["value"].cummax()

    max_seen_drawdown = df["drawdown"].min()
    return max_seen_drawdown
