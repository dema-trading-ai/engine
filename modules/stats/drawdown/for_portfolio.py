import pandas as pd
import empyrical as ep

from modules.stats.drawdown.drawdown import get_max_drawdown_ratio


def get_max_seen_drawdown_for_portfolio(capital_per_timestamp: dict):
    max_seen_drawdown = {}

    df = pd.DataFrame.from_dict(capital_per_timestamp, columns=['value'], orient='index')
    df["drawdown"] = df["value"] / df["value"].cummax()

    max_seen_drawdown["drawdown"] = df["drawdown"].min()
    max_seen_drawdown["at"] = df["drawdown"].idxmin()
    max_seen_drawdown["from"] = df.loc[:max_seen_drawdown["at"]].value.idxmax()
    df_after_max_drawdown = df.loc[max_seen_drawdown["at"]:]
    df_after_recovery = df_after_max_drawdown.loc[df_after_max_drawdown["drawdown"] == 1]

    if len(df_after_recovery) > 0:
        max_seen_drawdown["to"] = df_after_recovery.index[0]
    else:
        max_seen_drawdown["to"] = 0

    # if drawdown is from the very first timestep
    if max_seen_drawdown["from"] == 0:
        max_seen_drawdown["from"] = df.index[1]

    return max_seen_drawdown


def get_max_realised_drawdown_for_portfolio(realised_profits_per_timestamp: dict):
    df = pd.DataFrame.from_dict(realised_profits_per_timestamp, columns=['value'], orient='index')
    max_realised_drawdown = get_max_drawdown_ratio(df)

    return max_realised_drawdown


def get_sharpe_ratio(capital_per_timestamp: dict) -> float:
    # capital = pd.Series(capital_per_timestamp.values())
    df = pd.DataFrame.from_dict(capital_per_timestamp, columns=['value'], orient='index')
    df.drop(labels=0, inplace=True)
    df['index_1'] = df.index
    df['index_1'] = pd.to_datetime(df['index_1'], unit='ms')
    df.set_index('index_1', drop=True, inplace=True)
    df1 = df.resample('D').sum()
    print(df1)
    returns = []
    capital_list = list(capital_per_timestamp.values())
    for capital in capital_list:
        if capital_list.index(capital) == 0:
            diff = 0
        else:
            diff = (capital / capital_list[capital_list.index(capital) - 1]) - 1
        returns.append(diff)
    df = pd.Series(returns)
    sharpe_ratio = ep.sharpe_ratio(df)
    return sharpe_ratio
