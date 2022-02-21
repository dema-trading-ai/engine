import pandas as pd
from datetime import datetime


def convert_timestamp_dict_to_dataframe(per_timestamp_dict: dict, resample: bool = False) -> pd.DataFrame:
    """
    Converts a dict of capital per timestamps to a dataframe with timestamps as index, and with a daily returns column.
    Standardizes the dataframe used for ratio computation.
    """

    df = pd.DataFrame.from_dict(per_timestamp_dict, columns=['capital'], orient='index')

    if len(df['capital']) > 1:  # Don't run the conversion if the df has only one item

        df.index = [datetime.fromtimestamp(date / 1000) for date in df.index]
        if resample:
            df = df.resample('D').apply(lambda x: x.iloc[-1])

    return df
