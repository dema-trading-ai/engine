from datetime import datetime
from pandas import DataFrame
from modules.stats.metrics.profit_ratio import with_copied_initial_row


def get_market_ratio_per_coin(signal_dict):
    df = DataFrame(signal_dict.values()).set_index("time")
    df = with_copied_initial_row(df)
    df["close"] = df["close"].fillna(value=None, method='ffill')
    df["market_ratio"] = (df["close"] / df["close"].shift(1))
    df["market_ratio"] = df["market_ratio"].fillna(value=1)
    return df["market_ratio"]


def get_market_ratios(signal_dict: dict) -> DataFrame:
    coins = list(signal_dict.keys())
    market_ratio = {}
    for coin in coins:
        market_ratio[coin] = get_market_ratio_per_coin(signal_dict[coin])
    market_ratio_first_coin = market_ratio[coins[0]]

    # Combine market change of multiple coins into one dataframe
    combined_market_ratio_df = DataFrame(market_ratio_first_coin).rename(columns={"market_ratio": coins[0]})
    for coin in coins[1:]:
        combined_market_ratio_df[coin] = market_ratio[coin]

    combined_market_ratio_df['avg_market_ratio'] = combined_market_ratio_df.mean(axis=1)
    return combined_market_ratio_df


def get_outperforming_timeframe(cum_profit_ratio: DataFrame, market_ratio_df: DataFrame, timeframe="W"):
    # copy dataframes so the originals don't get modified
    cum_profit_ratio = cum_profit_ratio.copy()
    market_ratio_df = market_ratio_df.copy()

    # Refactor index of dataframes
    datetime_index = [datetime.fromtimestamp(ms / 1000.0) for ms in market_ratio_df.index]
    market_ratio_df.index = datetime_index
    cum_profit_ratio.index = datetime_index

    # Resample dataframes to timeframe
    close_price = market_ratio_df.resample(timeframe, origin='start').ohlc()
    market_change = close_price['close'] / close_price['open']

    capital = cum_profit_ratio['value'] * 1000
    cum_profit_ratio = capital.resample(timeframe, origin='start').ohlc()
    capital = cum_profit_ratio['close'] / cum_profit_ratio['open']

    # Define the winning weeks
    wins = len(capital[capital > market_change + 0.001])
    losses = len(capital[capital < market_change - 0.001])
    draws = len(capital) - wins - losses

    return wins, draws, losses


def get_profitable_timeframe(cum_profit_ratio, timeframe="W"):
    # copy dataframes so the originals don't get modified
    cum_profit_ratio = cum_profit_ratio.copy()
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
