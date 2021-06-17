import pandas as pd


def get_max_seen_drawdown_for_portfolio(capital_per_timestamp: dict):
    max_seen_drawdown = {
        "from": 0,
        "to": 0,
        "at": 0,
        "drawdown": 1.0  # ratio
    }

    df = pd.DataFrame.from_dict(capital_per_timestamp, columns=['value'], orient='index')
    df["drawdown"] = (df["value"] - df["value"].cummax()) / df["value"].cummax()

    max_seen_drawdown["drawdown"] = df["drawdown"].min()
    max_seen_drawdown["at"] = df["drawdown"].idxmin()
    max_seen_drawdown["from"] = df.loc[:max_seen_drawdown["at"]].value.idxmax()
    max_seen_drawdown["to"] = df.loc[max_seen_drawdown["at"]:].drawdown.eq(0.0).idxmax()

    return max_seen_drawdown
