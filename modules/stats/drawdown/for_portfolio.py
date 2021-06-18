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


def get_max_realised_drawdown_for_portfolio(realised_profits_per_timestamp: dict):
    max_realised_drawdown = {
        "drawdown": 1.0,  # ratio
        "max_consecutive_losses": 0,
        "losing_trades": 0
    }

    df = pd.DataFrame.from_dict(realised_profits_per_timestamp, columns=['value'], orient='index')
    df["drawdown"] = (df["value"] - df["value"].cummax()) / df["value"].cummax()
    df['losing_trade'] = df.value.lt(df.value.shift())

    df['consecutive_losses'] = df.losing_trade.cumsum()-df.losing_trade.cumsum().where(~df.losing_trade).ffill().fillna(0).astype(int)

    max_realised_drawdown['drawdown'] = df["drawdown"].min()
    max_realised_drawdown['losing_trades'] = df["losing_trade"].value_counts().loc[True]
    max_realised_drawdown['max_consecutive_losses'] = df["consecutive_losses"].max()

    return max_realised_drawdown
