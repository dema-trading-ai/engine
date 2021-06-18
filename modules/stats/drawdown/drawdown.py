import pandas as pd


def get_max_drawdown_ratio(df: pd.DataFrame):
    """
    @param df: with column["value"]
    """
    df["drawdown_ratio"] = df["value"] / df["value"].cummax()
    return df["drawdown_ratio"].min()
