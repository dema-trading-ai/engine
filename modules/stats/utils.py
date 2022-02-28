from datetime import datetime

from pandas import DataFrame


def convert_timestamp_dict_to_dataframe(per_timestamp_dict: dict, resample: bool = False) -> DataFrame:
    """
    Converts a dict of capital per timestamps to a dataframe with timestamps as index, and with a daily returns column.
    Standardizes the dataframe used for ratio computation.
    """

    df = DataFrame.from_dict(per_timestamp_dict, columns=['capital'], orient='index')

    if len(df['capital']) > 1:  # Don't run the conversion if the df has only one item

        df.index = [datetime.fromtimestamp(date / 1000) for date in df.index]
        if resample:
            df = df.resample('D').apply(lambda row: row.iloc[-1])

    return df
