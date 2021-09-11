import pandas as pd


def get_max_drawdown_ratio(df: pd.DataFrame):
    """
    @param df: with column["value"]
    """
    df["drawdown_ratio"] = df["value"] / df["value"].cummax()
    return df["drawdown_ratio"].min()


def get_max_drawdown_ratio_without_buy_rows(df: pd.DataFrame):
    """
    @param df: with column["value"]
    """
    df["drawdown_ratio"] = df["value"] / df["value"].cummax()
    ans = df.loc[df['buy'] == 0.0]["drawdown_ratio"].min()
    return ans


def get_max_drawdown_ratio_series(series: pd.Series):
    series = series / series.cummax()
    return series.min()
