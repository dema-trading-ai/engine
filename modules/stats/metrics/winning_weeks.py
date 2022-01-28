from datetime import datetime
from pandas import DataFrame

from modules.stats.metrics.profit_ratio import with_copied_initial_row


def get_market_ratio(signal_dict):
    df = DataFrame(signal_dict.values()).set_index("time")
    df = with_copied_initial_row(df)
    df["close"] = df["close"].fillna(value=None, method='ffill')
    df["market_ratio"] = (df["close"] / df["close"].shift(1))
    df["market_ratio"] = df["market_ratio"].fillna(value=1)
    return df


def get_outperforming_timeframe(signal_dict: dict, cum_profit_ratio: DataFrame, timeframe="W"):
    cum_profit_ratio = cum_profit_ratio.iloc[1:]
    market_ratio_df = get_market_ratio(signal_dict)
    market_ratio_df = market_ratio_df.iloc[1:]

    # Refactor index of dataframes
    datetime_index = [datetime.fromtimestamp(ms / 1000.0) for ms in market_ratio_df.index]
    market_ratio_df.index = datetime_index
    cum_profit_ratio.index = datetime_index

    # Resample dataframes to timeframe
    close_price = market_ratio_df['close'].resample(timeframe, origin='start').ohlc()
    market_change = close_price['close'] / close_price['open']

    capital = cum_profit_ratio['value'] * 1000
    cum_profit_ratio = capital.resample(timeframe, origin='start').ohlc()
    capital = cum_profit_ratio['close'] / cum_profit_ratio['open']

    # Define the winning weeks
    wins = len(capital[capital > market_change + 0.001])
    losses = len(capital[capital < market_change - 0.001])
    draws = len(capital) - wins - losses

    return wins, draws, losses, market_change


def get_profitable_timeframe(cum_profit_ratio, timeframe="W"):
    # Create dataframes
    cum_profit_ratio = cum_profit_ratio.iloc[1:]

    # Refactor index of dataframes
    datetime_index = [datetime.fromtimestamp(ms / 1000.0) for ms in cum_profit_ratio.index]
    cum_profit_ratio.index = datetime_index

    # Resample dataframes to one week
    capital = cum_profit_ratio['value'] * 1000
    capital = capital.resample(timeframe, origin='start').ohlc()
    capital_timeframe = \
        capital['close'] / capital['open']

    # Define the winning weeks
    wins = len(capital_timeframe[capital_timeframe > 1.001])
    losses = len(capital_timeframe[capital_timeframe < 0.999])
    draws = len(capital_timeframe) - wins - losses

    return wins, draws, losses
