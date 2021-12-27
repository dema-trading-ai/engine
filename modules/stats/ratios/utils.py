import pandas as pd


def change_capital_dict_to_dataframe(capital_per_timestamp: dict, risk_free: float) -> pd.DataFrame:
    """
    Converts a dict of capital per timestamps to a dataframe with timestamps as index, and with a daily returns column.
    Standardizes the dataframe used for ratio computation.
    """

    df = pd.DataFrame.from_dict(capital_per_timestamp, columns=['capital'], orient='index')

    first_value = df['capital'][0]
    df = df.iloc[1:, :]  # Removing first row for the index to be transformed to Datetime correctly

    df.index = pd.to_datetime(df.index, unit='ms')
    df = df.resample('D').apply(lambda x: x.iloc[-1])

    df.loc[df.index[0]] = first_value  # Replace with previous first value to include price of first buy in returns
    df = df.sort_index()

    df['returns'] = (df['capital'] - df['capital'].shift()) / 100
    df['risk_free'] = risk_free

    return df
